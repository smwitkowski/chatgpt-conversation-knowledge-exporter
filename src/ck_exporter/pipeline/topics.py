"""Topic discovery and labeling pipeline orchestration."""

import contextvars
import json
import logging
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from bertopic import BERTopic
from hdbscan import HDBSCAN
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from umap import UMAP

from ck_exporter.adapters.fs_jsonl import read_jsonl as _read_jsonl
from ck_exporter.config import get_topic_max_concurrency
from ck_exporter.core.models import Topic, TopicRegistry
from ck_exporter.core.ports.embedder import Embedder
from ck_exporter.core.ports.topic_labeler import TopicLabeler
from ck_exporter.logging import get_logger, should_show_progress
from ck_exporter.observability.langsmith import traceable_call, tracing_context
from ck_exporter.pipeline.io import (
    convert_claude_to_chatgpt,
    is_claude_conversation,
    load_conversations,
)

logger = get_logger(__name__)


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Read JSONL file and return list of objects."""
    return list(_read_jsonl(path))


def build_conversation_documents(
    input_path: Path,
    atoms_path: Path,
    limit: Optional[int] = None,
    include_kinds: Optional[List[str]] = None,
    exclude_kinds: Optional[List[str]] = None,
) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Build documents for each conversation by concatenating artifacts from universal atoms.

    Args:
        input_path: Path to conversation JSON file(s)
        atoms_path: Path to consolidated atoms.jsonl (universal format)
        limit: Optional limit on number of conversations to process
        include_kinds: Optional list of atom kinds to include (default: fact, decision, open_question)
        exclude_kinds: Optional list of atom kinds to exclude (default: action_item, meeting_topic, risk, blocker, dependency)

    Returns:
        Tuple of (conversation_documents, conversation_titles)
        - conversation_documents: dict mapping conversation_id to document text
        - conversation_titles: dict mapping conversation_id to title
    """
    # Default include/exclude kinds for topic discovery
    if include_kinds is None:
        include_kinds = ["fact", "decision", "open_question"]
    if exclude_kinds is None:
        exclude_kinds = ["action_item", "meeting_topic", "risk", "blocker", "dependency"]

    # Load conversations to get titles
    conversations = load_conversations(input_path, limit=limit)
    conversation_titles = {}
    conversation_projects: Dict[str, str] = {}
    for conv in conversations:
        # Handle Claude conversations that might not be converted yet
        if is_claude_conversation(conv):
            conv = convert_claude_to_chatgpt(conv)
        conv_id = conv.get("conversation_id") or conv.get("id") or conv.get("uuid", "")
        title = conv.get("title") or conv.get("name") or "Untitled Conversation"
        conversation_titles[conv_id] = title
        project_id = conv.get("project_id") or conv.get("project_uuid")
        project_name = conv.get("project_name")
        if not project_id and isinstance(conv.get("project"), dict):
            project_id = conv["project"].get("uuid")
        if not project_name and isinstance(conv.get("project"), dict):
            project_name = conv["project"].get("name")

        if project_name and project_id:
            conversation_projects[conv_id] = f"{project_name} ({project_id})"
        elif project_name:
            conversation_projects[conv_id] = str(project_name)
        elif project_id:
            conversation_projects[conv_id] = str(project_id)

    # Load consolidated universal atoms
    all_atoms = read_jsonl(atoms_path)

    # Filter atoms by kind
    filtered_atoms = []
    for atom in all_atoms:
        kind = atom.get("kind", "")
        if include_kinds and kind not in include_kinds:
            continue
        if exclude_kinds and kind in exclude_kinds:
            continue
        filtered_atoms.append(atom)

    # Group artifacts by conversation_id and kind
    facts_by_conv = defaultdict(list)
    decisions_by_conv = defaultdict(list)
    questions_by_conv = defaultdict(list)

    for atom in filtered_atoms:
        conv_id = atom.get("source_conversation_id", "")
        if not conv_id:
            continue
        kind = atom.get("kind", "")
        statement = atom.get("statement", "").strip()
        if not statement:
            continue

        if kind == "decision":
            decisions_by_conv[conv_id].append(statement)
        elif kind == "open_question":
            questions_by_conv[conv_id].append(statement)
        else:
            # Facts and other kinds
            facts_by_conv[conv_id].append(statement)

    # Build documents
    conversation_documents = {}
    all_conv_ids = (
        set(conversation_titles.keys())
        | set(facts_by_conv.keys())
        | set(decisions_by_conv.keys())
        | set(questions_by_conv.keys())
    )

    for conv_id in all_conv_ids:
        title = conversation_titles.get(conv_id, "Untitled Conversation")
        parts = [f"Title: {title}"]

        project_label = conversation_projects.get(conv_id)
        if project_label:
            parts.append(f"Project: {project_label}")

        fact_statements = facts_by_conv.get(conv_id, [])
        if fact_statements:
            parts.append("\nFacts and Knowledge:")
            parts.extend(f"- {stmt}" for stmt in fact_statements)

        decision_statements = decisions_by_conv.get(conv_id, [])
        if decision_statements:
            parts.append("\nDecisions:")
            parts.extend(f"- {stmt}" for stmt in decision_statements)

        question_texts = questions_by_conv.get(conv_id, [])
        if question_texts:
            parts.append("\nOpen Questions:")
            parts.extend(f"- {q}" for q in question_texts)

        conversation_documents[conv_id] = "\n".join(parts)

    return conversation_documents, conversation_titles


def _discover_topics_impl(
    documents: Dict[str, str],
    embedder: Embedder,
    target_topics: int = 50,
    use_pooling: bool = True,
    chunk_tokens: int = 600,
    overlap_tokens: int = 80,
    cache_dir: Optional[Path] = None,
) -> Tuple[BERTopic, np.ndarray, List[str]]:
    """
    Internal implementation of discover_topics (called via traceable_call wrapper).
    """
    if not documents:
        raise ValueError("No documents provided")

    doc_ids = list(documents.keys())
    doc_texts = [documents[conv_id] for conv_id in doc_ids]

    logger.info(
        "Generating embeddings for conversations",
        extra={
            "event": "topics.embeddings.start",
            "num_conversations": len(doc_texts),
            "use_pooling": use_pooling,
            "chunk_tokens": chunk_tokens if use_pooling else None,
        },
    )

    # Generate embeddings via embedder
    if use_pooling:
        embeddings = embedder.embed_pooled(
            doc_texts,
            chunk_tokens=chunk_tokens,
            overlap_tokens=overlap_tokens,
            cache_dir=cache_dir,
        )
    else:
        embeddings = embedder.embed(doc_texts)

    logger.info(
        "Generated embeddings",
        extra={
            "event": "topics.embeddings.complete",
            "shape": list(embeddings.shape),
            "embedding_dim": embeddings.shape[1] if len(embeddings.shape) > 1 else None,
        },
    )

    # Configure BERTopic with pre-computed embeddings
    # Gate verbose based on log level - only verbose if DEBUG/INFO logging is enabled
    bertopic_logger = logging.getLogger("bertopic")
    verbose = bertopic_logger.level <= logging.INFO

    umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric="cosine", random_state=42)
    hdbscan_model = HDBSCAN(min_cluster_size=2, metric="euclidean", cluster_selection_method="eom")

    logger.info(
        "Configuring BERTopic",
        extra={
            "event": "topics.bertopic.config",
            "target_topics": target_topics,
            "verbose": verbose,
        },
    )

    topic_model = BERTopic(
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        nr_topics=target_topics,
        min_topic_size=2,
        calculate_probabilities=False,
        verbose=verbose,
    )

    logger.info(
        "Running BERTopic clustering",
        extra={"event": "topics.bertopic.clustering.start"},
    )
    topics, probs = topic_model.fit_transform(doc_texts, embeddings=embeddings)

    num_topics = len(set(topics)) - (1 if -1 in topics else 0)  # Exclude outlier topic -1
    logger.info(
        "Discovered topics",
        extra={
            "event": "topics.bertopic.clustering.complete",
            "num_topics": num_topics,
            "num_outliers": list(topics).count(-1) if -1 in topics else 0,
        },
    )

    return topic_model, embeddings, doc_ids


def discover_topics(
    documents: Dict[str, str],
    embedder: Embedder,
    target_topics: int = 50,
    use_pooling: bool = True,
    chunk_tokens: int = 600,
    overlap_tokens: int = 80,
    cache_dir: Optional[Path] = None,
) -> Tuple[BERTopic, np.ndarray, List[str]]:
    """
    Discover topics using BERTopic with pre-computed embeddings.

    Args:
        documents: Dict mapping conversation_id to document text
        embedder: Embedder implementation
        target_topics: Target number of topics
        use_pooling: Whether to use chunked pooling (default True)
        chunk_tokens: Maximum tokens per chunk when pooling (default 600)
        overlap_tokens: Token overlap between chunks when pooling (default 80)
        cache_dir: Optional directory for caching embeddings

    Returns:
        Tuple of (bertopic_model, embeddings, doc_ids)
    """
    num_conversations = len(documents) if documents else 0
    embedding_model = getattr(embedder, "model", "unknown")
    
    return traceable_call(
        lambda: _discover_topics_impl(
            documents=documents,
            embedder=embedder,
            target_topics=target_topics,
            use_pooling=use_pooling,
            chunk_tokens=chunk_tokens,
            overlap_tokens=overlap_tokens,
            cache_dir=cache_dir,
        ),
        name="discover_topics",
        run_type="chain",
        metadata={
            "num_conversations": num_conversations,
            "target_topics": target_topics,
            "embedding_model": embedding_model,
        },
        tags=["topic_discovery"],
    )


def _label_single_topic(
    topic_id: int,
    topic_model: BERTopic,
    topics_out: np.ndarray,
    doc_ids: List[str],
    doc_texts: List[str],
    labeler: TopicLabeler,
) -> Optional[Topic]:
    """
    Label a single topic using LLM.

    Args:
        topic_id: Topic ID to label
        topic_model: Fitted BERTopic model
        topics_out: Topic assignments for each document
        doc_ids: List of conversation IDs
        doc_texts: List of document texts
        labeler: Topic labeler implementation

    Returns:
        Topic object or None if topic should be skipped
    """
    if topic_id == -1:  # Skip outlier topic
        return None

    # Get representative documents for this topic
    topic_docs = []
    for i, doc_topic in enumerate(topics_out):
        if doc_topic == topic_id:
            topic_docs.append((doc_ids[i], doc_texts[i]))

    # Take top 3 representative documents
    representative_docs = topic_docs[:3]
    if not representative_docs:
        return None

    # Get keywords from BERTopic
    topic_words = topic_model.get_topic(topic_id)
    keywords = [word for word, _ in topic_words[:10]] if topic_words else []

    # Label using labeler with tracing context
    with tracing_context(topic_id=topic_id):
        label_data = labeler.label_topic(topic_id, representative_docs, keywords)
    
    name = label_data.get("name", f"Topic {topic_id}")
    description = label_data.get("description", "No description available")

    # Get representative conversation IDs
    rep_conv_ids = [conv_id for conv_id, _ in representative_docs]

    return Topic(
        topic_id=topic_id,
        name=name,
        description=description,
        keywords=keywords,
        representative_conversations=rep_conv_ids,
    )


def _label_topics_with_llm_impl(
    topic_model: BERTopic,
    documents: Dict[str, str],
    doc_ids: List[str],
    doc_texts: List[str],
    labeler: TopicLabeler,
) -> List[Topic]:
    """
    Internal implementation of label_topics_with_llm (called via traceable_call wrapper).
    """
    # Get topic info from BERTopic
    topic_info = topic_model.get_topic_info()
    topics_out = topic_model.topics_

    logger.info(
        "Labeling topics with LLM",
        extra={
            "event": "topics.labeling.start",
            "num_topics": len(topic_info),
        },
    )

    # Collect valid topic IDs (excluding outlier -1)
    valid_topic_rows = []
    for idx, row in topic_info.iterrows():
        topic_id = int(row["Topic"])
        if topic_id != -1:
            valid_topic_rows.append((idx, topic_id))

    if not valid_topic_rows:
        logger.warning(
            "No valid topics to label",
            extra={"event": "topics.labeling.no_topics"},
        )
        return []

    max_concurrency = get_topic_max_concurrency()
    logger.debug(
        "Labeling topics with parallelization",
        extra={
            "event": "topics.labeling.parallel.start",
            "num_topics": len(valid_topic_rows),
            "max_concurrency": max_concurrency,
        },
    )

    # Progress bar will be rendered conditionally based on logging mode
    from rich.console import Console

    discovered_topics_dict: Dict[int, Topic] = {}

    if should_show_progress():
        console = Console(stderr=True)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Labeling topics", total=len(topic_info))

            # Process topics in parallel
            with ThreadPoolExecutor(max_workers=max_concurrency) as executor:
                futures: dict[Any, int] = {}
                for idx, topic_id in valid_topic_rows:
                    ctx = contextvars.copy_context()
                    future = executor.submit(ctx.run, _label_single_topic, topic_id, topic_model, topics_out, doc_ids, doc_texts, labeler)
                    futures[future] = (idx, topic_id)

                # Collect results as they complete
                completed_count = 0
                for future in as_completed(futures):
                    try:
                        topic = future.result()
                        idx, topic_id = futures[future]
                        if topic is not None:
                            discovered_topics_dict[topic_id] = topic
                        completed_count += 1
                        progress.update(task, advance=1)
                    except Exception as e:
                        idx, topic_id = futures[future]
                        logger.exception(
                            "Error labeling topic",
                            extra={
                                "event": "topics.labeling.error",
                                "topic_id": topic_id,
                            },
                        )
                        completed_count += 1
                        progress.update(task, advance=1)

                # Update progress for any skipped topics (outlier -1)
                skipped_count = len(topic_info) - len(valid_topic_rows)
                if skipped_count > 0:
                    progress.update(task, advance=skipped_count)
    else:
        # Non-interactive mode: process without progress bar
        with ThreadPoolExecutor(max_workers=max_concurrency) as executor:
            futures: dict[Any, int] = {}
            for idx, topic_id in valid_topic_rows:
                ctx = contextvars.copy_context()
                future = executor.submit(ctx.run, _label_single_topic, topic_id, topic_model, topics_out, doc_ids, doc_texts, labeler)
                futures[future] = topic_id

            # Collect results as they complete
            for future in as_completed(futures):
                try:
                    topic = future.result()
                    topic_id = futures[future]
                    if topic is not None:
                        discovered_topics_dict[topic_id] = topic
                except Exception as e:
                    topic_id = futures[future]
                    logger.exception(
                        "Error labeling topic",
                        extra={
                            "event": "topics.labeling.error",
                            "topic_id": topic_id,
                        },
                    )

    # Sort topics by topic_id for deterministic ordering
    discovered_topics = [discovered_topics_dict[topic_id] for topic_id in sorted(discovered_topics_dict.keys())]

    logger.info(
        "Labeled topics with LLM",
        extra={
            "event": "topics.labeling.complete",
            "num_labeled": len(discovered_topics),
        },
    )

    return discovered_topics


def label_topics_with_llm(
    topic_model: BERTopic,
    documents: Dict[str, str],
    doc_ids: List[str],
    doc_texts: List[str],
    labeler: TopicLabeler,
) -> List[Topic]:
    """
    Label discovered topics using LLM.

    Args:
        topic_model: Fitted BERTopic model
        documents: Dict mapping conversation_id to document text
        doc_ids: List of conversation IDs in same order as doc_texts
        doc_texts: List of document texts
        labeler: Topic labeler implementation

    Returns:
        List of Topic objects with names and descriptions
    """
    topic_info = topic_model.get_topic_info()
    num_topics = len([row for _, row in topic_info.iterrows() if int(row["Topic"]) != -1])
    
    return traceable_call(
        lambda: _label_topics_with_llm_impl(
            topic_model=topic_model,
            documents=documents,
            doc_ids=doc_ids,
            doc_texts=doc_texts,
            labeler=labeler,
        ),
        name="label_topics_with_llm",
        run_type="chain",
        metadata={
            "num_topics": num_topics,
        },
        tags=["topic_labeling"],
    )


def save_topic_registry(
    topics: List[Topic],
    topic_model: BERTopic,
    embeddings: np.ndarray,
    topics_out: np.ndarray,
    doc_ids: List[str],
    embedding_model: str,
    output_path: Path,
) -> None:
    """
    Save topic registry with centroid embeddings.

    Args:
        topics: List of Topic objects
        topic_model: Fitted BERTopic model
        embeddings: Document embeddings array
        topics_out: Topic assignments for each document
        doc_ids: List of conversation IDs
        embedding_model: Model identifier
        output_path: Path to save registry JSON
    """
    # Calculate centroid embeddings for each topic
    topic_centroids = {}
    for topic in topics:
        topic_id = topic.topic_id
        # Get embeddings for documents in this topic
        topic_emb_indices = [i for i, t in enumerate(topics_out) if t == topic_id]
        if topic_emb_indices:
            topic_embeddings = embeddings[topic_emb_indices]
            centroid = np.mean(topic_embeddings, axis=0)
            topic_centroids[topic_id] = centroid.tolist()

    # Add centroid embeddings to topics
    for topic in topics:
        if topic.topic_id in topic_centroids:
            topic.centroid_embedding = topic_centroids[topic.topic_id]

    from datetime import datetime

    registry = TopicRegistry(
        generated_at=datetime.now().isoformat(),
        embedding_model=embedding_model,
        num_topics=len(topics),
        topics=topics,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(registry.model_dump(), f, indent=2, ensure_ascii=False)

    logger.info(
        "Saved topic registry",
        extra={
            "event": "topics.registry.saved",
            "output_path": str(output_path),
            "num_topics": len(topics),
            "embedding_model": embedding_model,
        },
    )
