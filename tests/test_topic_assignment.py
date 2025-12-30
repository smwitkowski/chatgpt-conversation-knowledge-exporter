"""Tests for topic assignment threshold logic."""

import numpy as np
import pytest

from ck_exporter.embeddings import cosine_similarity


def test_cosine_similarity_identical():
    """Test cosine similarity for identical vectors."""
    vec = np.array([1.0, 2.0, 3.0])
    similarity = cosine_similarity(vec, vec)
    assert abs(similarity - 1.0) < 1e-6


def test_cosine_similarity_orthogonal():
    """Test cosine similarity for orthogonal vectors."""
    vec1 = np.array([1.0, 0.0, 0.0])
    vec2 = np.array([0.0, 1.0, 0.0])
    similarity = cosine_similarity(vec1, vec2)
    assert abs(similarity - 0.0) < 1e-6


def test_cosine_similarity_opposite():
    """Test cosine similarity for opposite vectors."""
    vec1 = np.array([1.0, 0.0])
    vec2 = np.array([-1.0, 0.0])
    similarity = cosine_similarity(vec1, vec2)
    assert abs(similarity - (-1.0)) < 1e-6 or similarity == 0.0  # Clamped to [0, 1]


def test_cosine_similarity_shape_mismatch():
    """Test cosine similarity raises error for mismatched shapes."""
    vec1 = np.array([1.0, 2.0])
    vec2 = np.array([1.0, 2.0, 3.0])
    with pytest.raises(ValueError, match="same shape"):
        cosine_similarity(vec1, vec2)


def test_cosine_similarity_zero_vector():
    """Test cosine similarity handles zero vectors."""
    vec1 = np.array([1.0, 2.0])
    vec2 = np.array([0.0, 0.0])
    similarity = cosine_similarity(vec1, vec2)
    assert similarity == 0.0


def test_cosine_similarity_normalized():
    """Test cosine similarity returns values in [0, 1] range."""
    vec1 = np.array([1.0, 2.0, 3.0])
    vec2 = np.array([4.0, 5.0, 6.0])
    similarity = cosine_similarity(vec1, vec2)
    assert 0.0 <= similarity <= 1.0
