"""Embedder port interface."""

from pathlib import Path
from typing import Protocol

import numpy as np


class Embedder(Protocol):
    """Interface for text embedding services."""

    def embed(self, texts: list[str], batch_size: int = 100) -> np.ndarray:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of text strings to embed
            batch_size: Maximum texts per API call (default 100)

        Returns:
            numpy array of shape (n_texts, embedding_dim)
        """
        ...

    def embed_pooled(
        self,
        texts: list[str],
        chunk_tokens: int = 600,
        overlap_tokens: int = 80,
        pooling: str = "mean",
        cache_dir: Path | None = None,
        batch_size: int = 100,
    ) -> np.ndarray:
        """
        Generate pooled embeddings for texts by chunking, embedding chunks, and pooling.

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
        ...
