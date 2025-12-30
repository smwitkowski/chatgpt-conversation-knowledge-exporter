"""Tests for embedding pooling functionality."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from ck_exporter.embeddings import EmbeddingClient, POOLING_VERSION


class MockEmbeddingResponse:
    """Mock response from OpenAI embeddings API."""

    def __init__(self, embeddings):
        self.data = [MagicMock(embedding=emb) for emb in embeddings]


def test_normalized_mean_pool_single_chunk():
    """Test pooling with a single chunk (should just normalize)."""
    client = EmbeddingClient(model="openai/text-embedding-3-small", use_openrouter=False)

    # Create a test embedding (not normalized)
    chunk_emb = np.array([1.0, 2.0, 3.0])
    chunk_embeddings = chunk_emb.reshape(1, -1)

    pooled = client._normalized_mean_pool(chunk_embeddings)

    # Should be normalized
    norm = np.linalg.norm(pooled)
    assert abs(norm - 1.0) < 1e-6

    # Should be proportional to original
    expected = chunk_emb / np.linalg.norm(chunk_emb)
    np.testing.assert_allclose(pooled, expected, rtol=1e-6)


def test_normalized_mean_pool_multiple_chunks():
    """Test pooling with multiple chunks."""
    client = EmbeddingClient(model="openai/text-embedding-3-small", use_openrouter=False)

    # Create multiple chunk embeddings
    chunk1 = np.array([1.0, 0.0, 0.0])
    chunk2 = np.array([0.0, 1.0, 0.0])
    chunk3 = np.array([0.0, 0.0, 1.0])
    chunk_embeddings = np.array([chunk1, chunk2, chunk3])

    pooled = client._normalized_mean_pool(chunk_embeddings)

    # Should be normalized
    norm = np.linalg.norm(pooled)
    assert abs(norm - 1.0) < 1e-6

    # Should be mean of normalized chunks, then normalized
    expected = (chunk1 + chunk2 + chunk3) / 3
    expected = expected / np.linalg.norm(expected)
    np.testing.assert_allclose(pooled, expected, rtol=1e-6)


def test_normalized_mean_pool_zero_chunks():
    """Test pooling raises error for empty chunks."""
    client = EmbeddingClient(model="openai/text-embedding-3-small", use_openrouter=False)

    with pytest.raises(ValueError, match="Cannot pool empty"):
        client._normalized_mean_pool(np.array([]).reshape(0, 10))


def test_get_cache_key():
    """Test cache key generation."""
    client = EmbeddingClient(model="openai/text-embedding-3-small", use_openrouter=False)

    key1 = client._get_cache_key("test text", POOLING_VERSION)
    key2 = client._get_cache_key("test text", POOLING_VERSION)
    key3 = client._get_cache_key("different text", POOLING_VERSION)

    # Same text should produce same key
    assert key1 == key2

    # Different text should produce different key
    assert key1 != key3

    # Key should be hex string (sha256)
    assert len(key1) == 64
    assert all(c in "0123456789abcdef" for c in key1)


def test_cache_save_and_load():
    """Test saving and loading embeddings from cache."""
    client = EmbeddingClient(model="openai/text-embedding-3-small", use_openrouter=False)

    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir)
        cache_key = "test_key_123"
        test_embedding = np.array([1.0, 2.0, 3.0])

        # Save to cache
        client._save_to_cache(cache_dir, cache_key, test_embedding)

        # Verify file exists
        cache_file = cache_dir / f"{cache_key}.npy"
        assert cache_file.exists()

        # Load from cache
        loaded = client._load_from_cache(cache_dir, cache_key)
        assert loaded is not None
        np.testing.assert_array_equal(loaded, test_embedding)

        # Non-existent key should return None
        missing = client._load_from_cache(cache_dir, "nonexistent")
        assert missing is None


def test_get_embeddings_pooled_shape():
    """Test that pooled embeddings have correct shape."""
    # Mock the API client to avoid actual API calls
    with patch.object(EmbeddingClient, "_get_embeddings_batch") as mock_batch:
        # Mock response: return embeddings of shape (batch_size, 1536) for text-embedding-3-small
        embedding_dim = 1536

        def mock_batch_side_effect(texts):
            return np.random.randn(len(texts), embedding_dim)

        mock_batch.side_effect = mock_batch_side_effect

        client = EmbeddingClient(model="openai/text-embedding-3-small", use_openrouter=False)

        # Test with texts that will be chunked
        texts = [
            "This is a short text.",
            "This is a longer text that might need chunking if it exceeds the token limit. " * 100,
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            embeddings = client.get_embeddings_pooled(
                texts, chunk_tokens=600, overlap_tokens=80, cache_dir=cache_dir
            )

            # Should return shape (n_texts, embedding_dim)
            assert embeddings.shape == (2, embedding_dim)

            # Each pooled embedding should be normalized (norm ≈ 1.0)
            for i in range(embeddings.shape[0]):
                norm = np.linalg.norm(embeddings[i])
                assert abs(norm - 1.0) < 1e-5, f"Embedding {i} not normalized: norm={norm}"


def test_get_embeddings_pooled_cache_hit():
    """Test that cached embeddings are used instead of API calls."""
    with patch.object(EmbeddingClient, "_get_embeddings_batch") as mock_batch:
        embedding_dim = 1536
        call_count = {"count": 0}

        def mock_batch_side_effect(texts):
            call_count["count"] += 1
            return np.random.randn(len(texts), embedding_dim)

        mock_batch.side_effect = mock_batch_side_effect

        client = EmbeddingClient(model="openai/text-embedding-3-small", use_openrouter=False)

        text = "This is a test text that will be cached."

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)

            # First call: should hit API
            embeddings1 = client.get_embeddings_pooled(
                [text], chunk_tokens=600, overlap_tokens=80, cache_dir=cache_dir
            )
            assert call_count["count"] > 0

            # Second call: should use cache (no new API calls)
            initial_count = call_count["count"]
            embeddings2 = client.get_embeddings_pooled(
                [text], chunk_tokens=600, overlap_tokens=80, cache_dir=cache_dir
            )
            assert call_count["count"] == initial_count  # No new calls

            # Embeddings should be identical
            np.testing.assert_array_equal(embeddings1, embeddings2)


def test_get_embeddings_pooled_empty_texts():
    """Test pooling with empty text list."""
    client = EmbeddingClient(model="openai/text-embedding-3-small", use_openrouter=False)

    embeddings = client.get_embeddings_pooled([])
    assert embeddings.shape == (0,)


def test_get_embeddings_pooled_unsupported_pooling():
    """Test that unsupported pooling methods raise error."""
    client = EmbeddingClient(model="openai/text-embedding-3-small", use_openrouter=False)

    with pytest.raises(ValueError, match="Unsupported pooling method"):
        client.get_embeddings_pooled(["test"], pooling="max")


def test_get_embeddings_pooled_no_cache():
    """Test pooling works without cache directory."""
    with patch.object(EmbeddingClient, "_get_embeddings_batch") as mock_batch:
        embedding_dim = 1536

        def mock_batch_side_effect(texts):
            return np.random.randn(len(texts), embedding_dim)

        mock_batch.side_effect = mock_batch_side_effect

        client = EmbeddingClient(model="openai/text-embedding-3-small", use_openrouter=False)

        texts = ["Test text 1", "Test text 2"]
        embeddings = client.get_embeddings_pooled(texts, cache_dir=None)

        assert embeddings.shape == (2, embedding_dim)
