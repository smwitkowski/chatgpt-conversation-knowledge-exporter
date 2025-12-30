"""Multi-label topic assignment for conversations."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from ck_exporter.core.models import ConversationTopics, TopicAssignment, TopicRegistry
from ck_exporter.embeddings import EmbeddingClient, cosine_similarity
from ck_exporter.logging import get_logger, with_context
from ck_exporter.pipeline.io import (
    convert_claude_to_chatgpt,
    is_claude_conversation,
    load_conversations,
)
from ck_exporter.pipeline.topics import build_conversation_documents, read_jsonl

logger = get_logger(__name__)


def load_topic_registry(registry_path: Path) -> TopicRegistry:
    """
    Load topic registry from JSON file.

    Args:
        registry_path: Path to topic_registry.json

    Returns:
        TopicRegistry object
    """
    if not registry_path.exists():
        raise FileNotFoundError(f"Topic registry not found: {registry_path}")

    with registry_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return TopicRegistry(**data)


def assign_topics(
    input_path: Path,
    atoms_path: Path,
    decisions_path: Path,
    questions_path: Path,
    registry: TopicRegistry,
    embedding_model: str = "openai/text-embedding-3-small",
    primary_threshold: float = 0.60,
    secondary_threshold: float = 0.55,
    use_openrouter: bool = True,
    use_pooling: bool = True,
    chunk_tokens: int = 600,
    overlap_tokens: int = 80,
    cache_dir: Optional[Path] = None,
    limit: Optional[int] = None,
) -> List[ConversationTopics]:
    """
    Assign topics to conversations using cosine similarity.

    Args:
        input_path: Path to conversation JSON file(s)
        atoms_path: Path to consolidated atoms.jsonl
        decisions_path: Path to consolidated decisions.jsonl
        questions_path: Path to consolidated open_questions.jsonl
        registry: TopicRegistry with discovered topics
        embedding_model: OpenRouter model identifier
        primary_threshold: Minimum score for primary topic
        secondary_threshold: Minimum score for secondary topics
        use_openrouter: Whether to use OpenRouter
        use_pooling: Whether to use chunked pooling (default True)
        chunk_tokens: Maximum tokens per chunk when pooling (default 600)
        overlap_tokens: Token overlap between chunks when pooling (default 80)
        cache_dir: Optional directory for caching embeddings
        limit: Optional limit on number of conversations to process

    Returns:
        List of ConversationTopics assignments
    """
    # Validate that embedding model matches registry
    if registry.embedding_model != embedding_model:
        logger.warning(
            "Embedding model mismatch",
            extra={
                "event": "assignment.model_mismatch",
                "registry_model": registry.embedding_model,
                "assignment_model": embedding_model,
            },
        )
    # Build conversation documents
    documents, titles = build_conversation_documents(
        input_path, atoms_path, decisions_path, questions_path
    )

    if not documents:
        logger.warning(
            "No conversations found",
            extra={"event": "assignment.empty"},
        )
        return []

    # Build conversation metadata map (project id/name when available)
    project_meta: Dict[str, Dict[str, str]] = {}
    try:
        conversations = load_conversations(input_path, limit=limit)
        for conv in conversations:
            if is_claude_conversation(conv):
                conv = convert_claude_to_chatgpt(conv)
            conv_id = conv.get("conversation_id") or conv.get("id") or conv.get("uuid", "")
            if not conv_id:
                continue

            project_id = conv.get("project_id") or conv.get("project_uuid")
            project_name = conv.get("project_name")
            if not project_id and isinstance(conv.get("project"), dict):
                project_id = conv["project"].get("uuid")
            if not project_name and isinstance(conv.get("project"), dict):
                project_name = conv["project"].get("name")

            meta: Dict[str, str] = {}
            if project_id:
                meta["project_id"] = str(project_id)
            if project_name:
                meta["project_name"] = str(project_name)
            if meta:
                project_meta[conv_id] = meta
    except Exception:
        # Metadata is optional; assignment can proceed without it.
        project_meta = {}

    # Count atoms per conversation for metadata
    atoms = read_jsonl(atoms_path)
    atom_counts = {}
    for atom in atoms:
        conv_id = atom.get("source_conversation_id", "")
        if conv_id:
            atom_counts[conv_id] = atom_counts.get(conv_id, 0) + 1

    # Generate embeddings for all conversations
    logger.info(
        "Generating embeddings",
        extra={
            "event": "assignment.embeddings.start",
            "num_conversations": len(documents),
            "use_pooling": use_pooling,
        },
    )
    embedding_client = EmbeddingClient(model=embedding_model, use_openrouter=use_openrouter)

    conv_ids = list(documents.keys())
    doc_texts = [documents[conv_id] for conv_id in conv_ids]
    if use_pooling:
        conv_embeddings = embedding_client.get_embeddings_pooled(
            doc_texts,
            chunk_tokens=chunk_tokens,
            overlap_tokens=overlap_tokens,
            cache_dir=cache_dir,
        )
    else:
        conv_embeddings = embedding_client.get_embeddings(doc_texts)

    logger.info(
        "Generated embeddings",
        extra={
            "event": "assignment.embeddings.complete",
            "shape": list(conv_embeddings.shape),
        },
    )

    # Get topic centroids
    topic_centroids = {}
    for topic in registry.topics:
        if topic.centroid_embedding:
            topic_centroids[topic.topic_id] = np.array(topic.centroid_embedding)

    if not topic_centroids:
        logger.error(
            "No topic centroids found in registry",
            extra={"event": "assignment.error", "reason": "no_centroids"},
        )
        return []

    # Assign topics to each conversation
    assignments = []
    logger.info(
        "Assigning topics to conversations",
        extra={"event": "assignment.start"},
    )

    for i, conv_id in enumerate(conv_ids):
        conv_embedding = conv_embeddings[i]
        title = titles.get(conv_id, "Untitled Conversation")
        meta = project_meta.get(conv_id, {})

        # Compute similarity to all topic centroids
        similarities = []
        for topic_id, centroid in topic_centroids.items():
            try:
                score = cosine_similarity(conv_embedding, centroid)
                topic_name = next((t.name for t in registry.topics if t.topic_id == topic_id), f"Topic {topic_id}")
                similarities.append((topic_id, topic_name, score))
            except Exception as e:
                logger.warning(
                    "Error computing similarity for topic",
                    extra={
                        "event": "assignment.similarity.error",
                        "topic_id": topic_id,
                    },
                    exc_info=True,
                )
                continue

        # Sort by score descending
        similarities.sort(key=lambda x: x[2], reverse=True)

        if not similarities:
            # No valid similarities, create empty assignment
            assignments.append(
                ConversationTopics(
                    conversation_id=conv_id,
                    title=title,
                    project_id=meta.get("project_id"),
                    project_name=meta.get("project_name"),
                    topics=[],
                    atom_count=atom_counts.get(conv_id, 0),
                    review_flag=True,
                )
            )
            continue

        # Primary topic: always assign top-scoring topic
        primary_id, primary_name, primary_score = similarities[0]
        topic_assignments = [
            TopicAssignment(
                topic_id=primary_id,
                name=primary_name,
                score=primary_score,
                rank="primary",
            )
        ]

        # Secondary topics: any topic with score >= secondary_threshold
        # and within 0.25 of primary score
        for topic_id, topic_name, score in similarities[1:]:
            if score >= secondary_threshold and (primary_score - score) <= 0.25:
                topic_assignments.append(
                    TopicAssignment(
                        topic_id=topic_id,
                        name=topic_name,
                        score=score,
                        rank="secondary",
                    )
                )

        # Review flag: set if primary score is low or if secondary is very close to primary
        review_flag = False
        if primary_score < primary_threshold:
            review_flag = True
        elif len(similarities) > 1:
            secondary_score = similarities[1][2]
            if secondary_score >= secondary_threshold and (primary_score - secondary_score) < 0.08:
                review_flag = True

        assignments.append(
            ConversationTopics(
                conversation_id=conv_id,
                title=title,
                project_id=meta.get("project_id"),
                project_name=meta.get("project_name"),
                topics=topic_assignments,
                atom_count=atom_counts.get(conv_id, 0),
                review_flag=review_flag,
            )
            )

    logger.info(
        "Assigned topics to conversations",
        extra={
            "event": "assignment.complete",
            "num_assignments": len(assignments),
        },
    )
    return assignments


def save_assignments(assignments: List[ConversationTopics], output_path: Path) -> None:
    """
    Save topic assignments to JSONL file.

    Args:
        assignments: List of ConversationTopics assignments
        output_path: Path to save assignments.jsonl
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for assignment in assignments:
            # Convert to dict for JSON serialization
            assignment_dict = assignment.model_dump(exclude_none=True)
            f.write(json.dumps(assignment_dict, ensure_ascii=False) + "\n")

    logger.info(
        "Saved assignments",
        extra={
            "event": "assignment.saved",
            "output_path": str(output_path),
            "num_assignments": len(assignments),
        },
    )

    # Also create review queue for flagged items
    review_items = [a for a in assignments if a.review_flag]
    if review_items:
        review_path = output_path.parent / "review_queue.jsonl"
        with review_path.open("w", encoding="utf-8") as f:
            for assignment in review_items:
                primary = next((t for t in assignment.topics if t.rank == "primary"), None)
                review_dict = {
                    "conversation_id": assignment.conversation_id,
                    "title": assignment.title,
                    "project_id": assignment.project_id,
                    "project_name": assignment.project_name,
                    "primary_topic": primary.name if primary else "None",
                    "primary_score": primary.score if primary else 0.0,
                    "reason": "low_confidence" if (primary and primary.score < 0.60) else "ambiguous",
                }
                # Keep output tidy for non-Claude exports
                f.write(json.dumps({k: v for k, v in review_dict.items() if v is not None}, ensure_ascii=False) + "\n")

        logger.info(
            "Created review queue",
            extra={
                "event": "assignment.review_queue",
                "review_path": str(review_path),
                "num_review_items": len(review_items),
            },
        )
