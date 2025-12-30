"""OpenRouter-backed embedder adapter."""

import hashlib
from pathlib import Path
from typing import Optional

import numpy as np
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from ck_exporter.adapters.openrouter_client import make_openrouter_client
from ck_exporter.utils.chunking import chunk_text
from ck_exporter.core.ports.embedder import Embedder

# Pooling version for cache invalidation
POOLING_VERSION = "v1"


class OpenRouterEmbedder:
    """OpenRouter-backed implementation of Embedder."""

    def __init__(
        self,
        model: str = "openai/text-embedding-3-small",
        use_openrouter: bool = True,
        client: Optional[OpenAI] = None,
    ):
        """
        Initialize embedding client.

        Args:
            model: Model identifier (OpenRouter format)
            use_openrouter: If True, use OpenRouter API; otherwise use standard OpenAI
            client: Optional pre-configured OpenAI client (for testing/sharing)
        """
        self.model = model
        self._client = client if client is not None else make_openrouter_client(use_openrouter)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _get_embeddings_batch(self, texts: list[str]) -> np.ndarray:
        """
        Get embeddings for a batch of texts (up to 100).

        Args:
            texts: List of text strings to embed

        Returns:
            numpy array of shape (n_texts, embedding_dim)
        """
        if not texts:
            return np.array([])

        try:
            response = self._client.embeddings.create(
                model=self.model,
                input=texts,
            )

            embeddings = [item.embedding for item in response.data]
            return np.array(embeddings)
        except Exception as e:
            raise RuntimeError(f"Failed to get embeddings: {e}") from e

    def embed(self, texts: list[str], batch_size: int = 100) -> np.ndarray:
        """
        Get embeddings for multiple texts, batching as needed.

        Args:
            texts: List of text strings to embed
            batch_size: Maximum texts per API call (default 100)

        Returns:
            numpy array of shape (n_texts, embedding_dim)
        """
        if not texts:
            return np.array([])

        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            batch_embeddings = self._get_embeddings_batch(batch)
            all_embeddings.append(batch_embeddings)

        if not all_embeddings:
            return np.array([])

        return np.vstack(all_embeddings)

    def _get_cache_key(self, text: str, pooling_version: str = POOLING_VERSION) -> str:
        """Generate cache key for a text chunk."""
        key_string = f"{self.model}:{pooling_version}:{text}"
        return hashlib.sha256(key_string.encode("utf-8")).hexdigest()

    def _load_from_cache(self, cache_dir: Path, cache_key: str) -> Optional[np.ndarray]:
        """Load embedding from cache if it exists."""
        if cache_dir is None:
            return None
        cache_file = cache_dir / f"{cache_key}.npy"
        if cache_file.exists():
            try:
                return np.load(cache_file)
            except Exception:
                return None
        return None

    def _save_to_cache(self, cache_dir: Path, cache_key: str, embedding: np.ndarray) -> None:
        """Save embedding to cache."""
        if cache_dir is None:
            return
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_file = cache_dir / f"{cache_key}.npy"
            np.save(cache_file, embedding)
        except Exception:
            # Cache failures shouldn't break the pipeline
            pass

    def _normalized_mean_pool(self, chunk_embeddings: np.ndarray) -> np.ndarray:
        """
        Pool chunk embeddings using normalized mean pooling.

        Args:
            chunk_embeddings: Array of shape (n_chunks, embedding_dim)

        Returns:
            Pooled vector of shape (embedding_dim,)
        """
        if len(chunk_embeddings) == 0:
            raise ValueError("Cannot pool empty chunk embeddings")
        if len(chunk_embeddings) == 1:
            # Single chunk: just normalize it
            vec = chunk_embeddings[0]
            norm = np.linalg.norm(vec)
            return vec / norm if norm > 0 else vec

        # L2-normalize each chunk vector
        norms = np.linalg.norm(chunk_embeddings, axis=1, keepdims=True)
        # Avoid division by zero
        norms = np.where(norms == 0, 1.0, norms)
        normalized = chunk_embeddings / norms

        # Mean pool
        pooled = np.mean(normalized, axis=0)

        # L2-normalize the final pooled vector
        pooled_norm = np.linalg.norm(pooled)
        if pooled_norm > 0:
            pooled = pooled / pooled_norm

        return pooled

    def _map_embedding_model_to_tokenizer(self, embedding_model: str) -> str:
        """
        Map embedding model name to a tiktoken-compatible model name.

        Args:
            embedding_model: Embedding model identifier (e.g., "openai/text-embedding-3-small")

        Returns:
            Tiktoken-compatible model name
        """
        # OpenAI embedding models use cl100k_base encoding (same as GPT-3.5/GPT-4)
        if "openai" in embedding_model.lower() or "text-embedding" in embedding_model.lower():
            return "gpt-4"
        # Default fallback
        return "gpt-4"

    def embed_pooled(
        self,
        texts: list[str],
        chunk_tokens: int = 600,
        overlap_tokens: int = 80,
        pooling: str = "mean",
        cache_dir: Optional[Path] = None,
        batch_size: int = 100,
    ) -> np.ndarray:
        """
        Get pooled embeddings for multiple texts by chunking, embedding chunks, and pooling.

        Args:
            texts: List of text strings to embed
            chunk_tokens: Maximum tokens per chunk (default 600)
            overlap_tokens: Token overlap between chunks (default 80)
            pooling: Pooling method ("mean" for normalized mean pooling)
            cache_dir: Optional directory for caching embeddings
            batch_size: Maximum chunks per API call (default 100)

        Returns:
            numpy array of shape (n_texts, embedding_dim)
        """
        if not texts:
            return np.array([])

        if pooling != "mean":
            raise ValueError(f"Unsupported pooling method: {pooling}. Only 'mean' is supported.")

        tokenizer_model = self._map_embedding_model_to_tokenizer(self.model)

        # Chunk all texts
        all_chunks = []
        chunk_to_doc_idx = []  # Maps chunk index to original document index

        for doc_idx, text in enumerate(texts):
            chunks = chunk_text(
                text,
                max_tokens=chunk_tokens,
                overlap_tokens=overlap_tokens,
                model=tokenizer_model,
            )
            # Filter out empty chunks
            chunks = [chunk for chunk in chunks if chunk.strip()]
            if not chunks:
                # Empty text: skip this document (will handle later)
                chunks = []
            all_chunks.extend(chunks)
            chunk_to_doc_idx.extend([doc_idx] * len(chunks))

        if not all_chunks:
            return np.array([])

        # Get embeddings for all chunks (with caching)
        chunk_embeddings_list = []
        chunks_to_embed = []
        chunk_indices_to_embed = []

        for chunk_idx, chunk in enumerate(all_chunks):
            cache_key = self._get_cache_key(chunk)
            cached_embedding = self._load_from_cache(cache_dir, cache_key)

            if cached_embedding is not None:
                chunk_embeddings_list.append((chunk_idx, cached_embedding))
            else:
                chunks_to_embed.append(chunk)
                chunk_indices_to_embed.append(chunk_idx)

        # Embed uncached chunks in batches
        if chunks_to_embed:
            all_new_embeddings = []
            for i in range(0, len(chunks_to_embed), batch_size):
                batch = chunks_to_embed[i : i + batch_size]
                batch_indices = chunk_indices_to_embed[i : i + batch_size]
                batch_embeddings = self._get_embeddings_batch(batch)

                # Save to cache
                for chunk_idx, embedding in zip(batch_indices, batch_embeddings):
                    chunk = all_chunks[chunk_idx]
                    cache_key = self._get_cache_key(chunk)
                    self._save_to_cache(cache_dir, cache_key, embedding)

                all_new_embeddings.append(batch_embeddings)

            if all_new_embeddings:
                new_embeddings = np.vstack(all_new_embeddings)
                for chunk_idx, embedding in zip(chunk_indices_to_embed, new_embeddings):
                    chunk_embeddings_list.append((chunk_idx, embedding))

        # Sort by chunk index to maintain order
        chunk_embeddings_list.sort(key=lambda x: x[0])
        chunk_embeddings_array = np.array([emb for _, emb in chunk_embeddings_list])

        # Group chunks by document and pool
        num_docs = len(texts)
        pooled_embeddings = []

        # Get embedding dimension from first chunk (if available)
        embedding_dim = None
        if len(chunk_embeddings_array) > 0:
            embedding_dim = chunk_embeddings_array.shape[1]

        for doc_idx in range(num_docs):
            # Find all chunks belonging to this document
            doc_chunk_indices = [
                i for i, orig_doc_idx in enumerate(chunk_to_doc_idx) if orig_doc_idx == doc_idx
            ]
            if not doc_chunk_indices:
                # No chunks for this doc (empty or filtered out)
                # Use a zero vector with same dimension as other embeddings
                if embedding_dim is not None:
                    zero_vec = np.zeros(embedding_dim)
                    pooled_embeddings.append(zero_vec)
                else:
                    # No embeddings at all - this is an edge case
                    # We'll need to get dimension from API, but for now skip
                    # This document will be missing from results
                    continue
            else:
                doc_chunk_embeddings = chunk_embeddings_array[doc_chunk_indices]
                pooled = self._normalized_mean_pool(doc_chunk_embeddings)
                pooled_embeddings.append(pooled)

        if not pooled_embeddings:
            return np.array([])

        return np.array(pooled_embeddings)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.

    Args:
        a: First vector (1D array)
        b: Second vector (1D array)

    Returns:
        Cosine similarity score between 0 and 1
    """
    if a.shape != b.shape:
        raise ValueError(f"Vectors must have same shape, got {a.shape} and {b.shape}")

    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    similarity = dot_product / (norm_a * norm_b)
    # Clamp to [0, 1] in case of floating point errors
    return max(0.0, min(1.0, similarity))
