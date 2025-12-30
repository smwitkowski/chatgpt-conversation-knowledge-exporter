"""Topic discovery using BERTopic with OpenRouter embeddings.

This module is a backward-compatible shim that delegates to the new pipeline architecture.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from bertopic import BERTopic
import numpy as np

from ck_exporter.adapters.openrouter_client import make_openrouter_client
from ck_exporter.bootstrap import build_embedder, build_topic_labeler
from ck_exporter.pipeline.topics import (
    build_conversation_documents,
    discover_topics as _discover_topics,
    label_topics_with_llm as _label_topics_with_llm,
    save_topic_registry,
    read_jsonl,
)
from ck_exporter.core.models import Topic, TopicRegistry

# Re-export for backward compatibility
__all__ = [
    "build_conversation_documents",
    "discover_topics",
    "label_topics_with_llm",
    "save_topic_registry",
    "read_jsonl",
]


def discover_topics(
    documents: Dict[str, str],
    embedding_model: str = "openai/text-embedding-3-small",
    target_topics: int = 50,
    use_openrouter: bool = True,
    use_pooling: bool = True,
    chunk_tokens: int = 600,
    overlap_tokens: int = 80,
    cache_dir: Optional[Path] = None,
) -> Tuple[BERTopic, np.ndarray, List[str]]:
    """
    Discover topics using BERTopic with pre-computed embeddings.

    This is a backward-compatible wrapper that creates adapters and calls the new pipeline.

    Args:
        documents: Dict mapping conversation_id to document text
        embedding_model: OpenRouter model identifier
        target_topics: Target number of topics
        use_openrouter: Whether to use OpenRouter
        use_pooling: Whether to use chunked pooling (default True)
        chunk_tokens: Maximum tokens per chunk when pooling (default 600)
        overlap_tokens: Token overlap between chunks when pooling (default 80)
        cache_dir: Optional directory for caching embeddings

    Returns:
        Tuple of (bertopic_model, embeddings, doc_ids)
    """
    # Build embedder using bootstrap
    shared_client = make_openrouter_client(use_openrouter)
    embedder = build_embedder(
        model=embedding_model,
        use_openrouter=use_openrouter,
        client=shared_client,
    )

    # Delegate to pipeline
    return _discover_topics(
        documents=documents,
        embedder=embedder,
        target_topics=target_topics,
        use_pooling=use_pooling,
        chunk_tokens=chunk_tokens,
        overlap_tokens=overlap_tokens,
        cache_dir=cache_dir,
    )


def label_topics_with_llm(
    topic_model: BERTopic,
    documents: Dict[str, str],
    doc_ids: List[str],
    doc_texts: List[str],
    embedding_model: str,
    use_openrouter: bool = True,
    label_model: Optional[str] = None,
) -> List[Topic]:
    """
    Label discovered topics using LLM.

    This is a backward-compatible wrapper that creates adapters and calls the new pipeline.

    Args:
        topic_model: Fitted BERTopic model
        documents: Dict mapping conversation_id to document text
        doc_ids: List of conversation IDs in same order as doc_texts
        doc_texts: List of document texts
        embedding_model: Embedding model used (for registry)
        use_openrouter: Whether to use OpenRouter
        label_model: LLM model for labeling (defaults to fast model)

    Returns:
        List of Topic objects with names and descriptions
    """
    # Build labeler using bootstrap (handles env var selection)
    shared_client = make_openrouter_client(use_openrouter)
    labeler = build_topic_labeler(
        label_model=label_model,
        use_openrouter=use_openrouter,
        shared_client=shared_client,
    )

    # Delegate to pipeline
    return _label_topics_with_llm(
        topic_model=topic_model,
        documents=documents,
        doc_ids=doc_ids,
        doc_texts=doc_texts,
        labeler=labeler,
    )
