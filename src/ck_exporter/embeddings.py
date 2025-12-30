"""OpenRouter-based embedding client for topic modeling.

This module is a backward-compatible shim that re-exports the new adapter with old method names.
"""

from pathlib import Path
from typing import Optional

import numpy as np

from ck_exporter.adapters.openrouter_embedder import (
    POOLING_VERSION,
    OpenRouterEmbedder,
    cosine_similarity,
)


class EmbeddingClient:
    """
    Backward-compatible wrapper around OpenRouterEmbedder.

    Provides old method names (get_embeddings, get_embeddings_pooled) for compatibility.
    """

    def __init__(
        self,
        model: str = "openai/text-embedding-3-small",
        use_openrouter: bool = True,
    ):
        """
        Initialize embedding client.

        Args:
            model: Model identifier (OpenRouter format)
            use_openrouter: If True, use OpenRouter API; otherwise use standard OpenAI
        """
        self._embedder = OpenRouterEmbedder(model=model, use_openrouter=use_openrouter)
        self.model = model

    def get_embeddings(self, texts: list[str], batch_size: int = 100) -> np.ndarray:
        """
        Get embeddings for multiple texts, batching as needed.

        Args:
            texts: List of text strings to embed
            batch_size: Maximum texts per API call (default 100)

        Returns:
            numpy array of shape (n_texts, embedding_dim)
        """
        return self._embedder.embed(texts, batch_size=batch_size)

    def get_embeddings_pooled(
        self,
        texts: list[str],
        chunk_tokens: int = 600,
        overlap_tokens: int = 80,
        cache_dir: Optional[Path] = None,
    ) -> np.ndarray:
        """
        Get pooled embeddings for multiple texts by chunking, embedding chunks, and pooling.

        Args:
            texts: List of text strings to embed
            chunk_tokens: Maximum tokens per chunk (default 600)
            overlap_tokens: Token overlap between chunks (default 80)
            cache_dir: Optional directory for caching embeddings

        Returns:
            numpy array of shape (n_texts, embedding_dim)
        """
        return self._embedder.embed_pooled(
            texts,
            chunk_tokens=chunk_tokens,
            overlap_tokens=overlap_tokens,
            pooling="mean",
            cache_dir=cache_dir,
        )


__all__ = ["EmbeddingClient", "cosine_similarity", "POOLING_VERSION"]
