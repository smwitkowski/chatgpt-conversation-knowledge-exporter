"""Unit tests for embedding pooling logic."""

import numpy as np
import pytest

from ck_exporter.adapters.openrouter_embedder import OpenRouterEmbedder


def test_normalized_mean_pool_single_chunk():
    """Test pooling with single chunk."""
    embedder = OpenRouterEmbedder(model="openai/text-embedding-3-small", use_openrouter=False)
    chunk_embeddings = np.array([[1.0, 2.0, 3.0]])
    pooled = embedder._normalized_mean_pool(chunk_embeddings)

    # Should be normalized
    norm = np.linalg.norm(pooled)
    assert abs(norm - 1.0) < 1e-6 or norm == 0


def test_normalized_mean_pool_multiple_chunks():
    """Test pooling with multiple chunks."""
    embedder = OpenRouterEmbedder(model="openai/text-embedding-3-small", use_openrouter=False)
    chunk_embeddings = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    pooled = embedder._normalized_mean_pool(chunk_embeddings)

    # Should be normalized
    norm = np.linalg.norm(pooled)
    assert abs(norm - 1.0) < 1e-6


def test_normalized_mean_pool_empty_raises():
    """Test that empty chunk embeddings raise ValueError."""
    embedder = OpenRouterEmbedder(model="openai/text-embedding-3-small", use_openrouter=False)
    with pytest.raises(ValueError, match="Cannot pool empty"):
        embedder._normalized_mean_pool(np.array([]).reshape(0, 3))


def test_normalized_mean_pool_zero_vector():
    """Test pooling with zero vector."""
    embedder = OpenRouterEmbedder(model="openai/text-embedding-3-small", use_openrouter=False)
    chunk_embeddings = np.array([[0.0, 0.0, 0.0]])
    pooled = embedder._normalized_mean_pool(chunk_embeddings)
    # Should return zero vector (not normalized, since norm is 0)
    assert np.allclose(pooled, [0.0, 0.0, 0.0])
