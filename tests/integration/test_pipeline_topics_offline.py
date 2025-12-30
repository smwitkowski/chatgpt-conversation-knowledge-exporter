"""Integration tests for topics pipeline (offline, using fake adapters).

Note: These tests require a minimum number of documents (typically 10+) for BERTopic/UMAP
to work properly. For smaller datasets, UMAP's spectral layout algorithm fails.
"""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest.mock import MagicMock

import numpy as np
import pytest
from bertopic import BERTopic

from ck_exporter.core.ports.embedder import Embedder
from ck_exporter.core.ports.topic_labeler import TopicLabeler
from ck_exporter.pipeline.topics import discover_topics, label_topics_with_llm, save_topic_registry


class FakeEmbedder:
    """Fake embedder that returns deterministic embeddings."""

    def embed(self, texts: list[str], batch_size: int = 100) -> np.ndarray:
        """Return deterministic embeddings based on text hash."""
        import hashlib

        embeddings = []
        for text in texts:
            # Create deterministic embedding from text hash
            hash_obj = hashlib.md5(text.encode())
            hash_bytes = hash_obj.digest()
            # Create 1536-dim embedding by repeating hash bytes and converting to float
            # Use a more stable approach: convert bytes to ints, then to floats
            hash_ints = [int(b) for b in hash_bytes]
            # Repeat pattern to fill 1536 dimensions
            pattern = hash_ints * (1536 // len(hash_ints) + 1)
            embedding = np.array(pattern[:1536], dtype=np.float32)
            # Scale to reasonable range and normalize
            embedding = (embedding - 128.0) / 128.0  # Center around 0, scale to [-1, 1]
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            else:
                # Fallback: use random-like but deterministic
                np.random.seed(hash(text) % 2**32)
                embedding = np.random.randn(1536).astype(np.float32)
                embedding = embedding / np.linalg.norm(embedding)
            embeddings.append(embedding)
        return np.array(embeddings)

    def embed_pooled(
        self,
        texts: list[str],
        chunk_tokens: int = 600,
        overlap_tokens: int = 80,
        pooling: str = "mean",
        cache_dir: Path | None = None,
        batch_size: int = 100,
    ) -> np.ndarray:
        """Return pooled embeddings (same as embed for simplicity)."""
        return self.embed(texts, batch_size=batch_size)


class FakeTopicLabeler:
    """Fake topic labeler that returns deterministic labels."""

    def label_topic(
        self,
        topic_id: int,
        representative_docs: list[tuple[str, str]],
        keywords: list[str],
    ) -> dict[str, str]:
        """Return deterministic label based on topic_id."""
        return {
            "name": f"Test Topic {topic_id}",
            "description": f"This is a test description for topic {topic_id} with keywords: {', '.join(keywords[:3])}",
        }


@pytest.fixture
def fake_embedder() -> Embedder:
    """Create a fake embedder."""
    return FakeEmbedder()


@pytest.fixture
def fake_labeler() -> TopicLabeler:
    """Create a fake topic labeler."""
    return FakeTopicLabeler()


@pytest.fixture
def sample_documents() -> dict[str, str]:
    """Create sample conversation documents (need at least 10+ for UMAP to work reliably)."""
    # Generate 12 documents to ensure UMAP works
    docs = {}
    topics = ["testing", "development", "deployment", "architecture", "monitoring", "quality"]
    for i in range(12):
        topic = topics[i % len(topics)]
        docs[f"conv-{i+1}"] = f"Title: Test Conversation {i+1}\n\nFacts and Knowledge:\n- Fact about {topic}\n- Another fact about {topic}"
    return docs


def test_discover_topics_creates_model(fake_embedder: Embedder, sample_documents: dict[str, str]):
    """Test that topic discovery creates a BERTopic model."""
    topic_model, embeddings, doc_ids = discover_topics(
        documents=sample_documents,
        embedder=fake_embedder,
        target_topics=3,
        use_pooling=False,
    )

    assert isinstance(topic_model, BERTopic)
    assert embeddings.shape[0] == len(sample_documents)
    assert len(doc_ids) == len(sample_documents)
    assert set(doc_ids) == set(sample_documents.keys())


def test_label_topics_with_llm_creates_topics(
    fake_embedder: Embedder, fake_labeler: TopicLabeler, sample_documents: dict[str, str]
):
    """Test that topic labeling creates Topic objects."""
    # First discover topics
    topic_model, embeddings, doc_ids = discover_topics(
        documents=sample_documents,
        embedder=fake_embedder,
        target_topics=3,
        use_pooling=False,
    )

    doc_texts = [sample_documents[conv_id] for conv_id in doc_ids]

    # Label topics
    topics = label_topics_with_llm(
        topic_model=topic_model,
        documents=sample_documents,
        doc_ids=doc_ids,
        doc_texts=doc_texts,
        labeler=fake_labeler,
    )

    assert len(topics) > 0
    for topic in topics:
        assert topic.topic_id >= 0  # Skip outlier topic -1
        assert topic.name.startswith("Test Topic")
        assert "description" in topic.description
        assert isinstance(topic.keywords, list)


def test_save_topic_registry_creates_file(
    fake_embedder: Embedder, fake_labeler: TopicLabeler, sample_documents: dict[str, str], tmp_path: Path
):
    """Test that saving topic registry creates a JSON file."""
    # Discover and label topics
    topic_model, embeddings, doc_ids = discover_topics(
        documents=sample_documents,
        embedder=fake_embedder,
        target_topics=3,
        use_pooling=False,
    )

    doc_texts = [sample_documents[conv_id] for conv_id in doc_ids]
    topics = label_topics_with_llm(
        topic_model=topic_model,
        documents=sample_documents,
        doc_ids=doc_ids,
        doc_texts=doc_texts,
        labeler=fake_labeler,
    )

    topics_out = topic_model.topics_
    registry_path = tmp_path / "topic_registry.json"

    # Save registry
    save_topic_registry(
        topics=topics,
        topic_model=topic_model,
        embeddings=embeddings,
        topics_out=topics_out,
        doc_ids=doc_ids,
        embedding_model="test-model",
        output_path=registry_path,
    )

    # Verify file exists and is valid JSON
    assert registry_path.exists()
    with registry_path.open() as f:
        registry_data = json.load(f)

    assert "num_topics" in registry_data
    assert "topics" in registry_data
    assert len(registry_data["topics"]) == len(topics)
    assert registry_data["embedding_model"] == "test-model"
