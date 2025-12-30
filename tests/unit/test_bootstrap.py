"""Unit tests for bootstrap wiring module."""

import os
from unittest.mock import MagicMock, patch

import pytest

from ck_exporter.bootstrap import build_atom_extractor, build_embedder, build_topic_labeler


@patch("ck_exporter.bootstrap.make_openrouter_client")
def test_build_embedder_creates_openrouter_embedder(mock_make_client):
    """Test that build_embedder creates OpenRouterEmbedder."""
    mock_client = MagicMock()
    mock_make_client.return_value = mock_client

    embedder = build_embedder(
        model="openai/text-embedding-3-small",
        use_openrouter=True,
    )

    assert embedder is not None
    assert hasattr(embedder, "embed")
    assert hasattr(embedder, "embed_pooled")
    mock_make_client.assert_called_once_with(True)


@patch("ck_exporter.bootstrap.make_openrouter_client")
def test_build_atom_extractor_defaults_to_openrouter(mock_make_client):
    """Test that build_atom_extractor defaults to OpenRouter when env var not set."""
    mock_client = MagicMock()
    mock_make_client.return_value = mock_client

    # Ensure env var is not set
    if "CKX_ATOM_REFINER_IMPL" in os.environ:
        del os.environ["CKX_ATOM_REFINER_IMPL"]

    extractor = build_atom_extractor(use_openrouter=True)

    assert extractor is not None
    assert hasattr(extractor, "extract_from_chunk")
    assert hasattr(extractor, "refine_atoms")
    # Should be OpenRouterAtomExtractor (not HybridAtomExtractor)
    assert extractor.__class__.__name__ == "OpenRouterAtomExtractor"


@patch("ck_exporter.bootstrap.make_openrouter_client")
@patch("ck_exporter.bootstrap.DspyAtomRefiner")
@patch("ck_exporter.bootstrap.HybridAtomExtractor")
def test_build_atom_extractor_uses_dspy_when_env_set(
    mock_hybrid_class, mock_dspy_refiner_class, mock_make_client
):
    """Test that build_atom_extractor uses DSPy when CKX_ATOM_REFINER_IMPL=dspy."""
    mock_client = MagicMock()
    mock_make_client.return_value = mock_client

    mock_dspy_refiner = MagicMock()
    mock_dspy_refiner_class.return_value = mock_dspy_refiner

    mock_hybrid = MagicMock()
    mock_hybrid_class.return_value = mock_hybrid

    # Set env var to request DSPy
    os.environ["CKX_ATOM_REFINER_IMPL"] = "dspy"

    try:
        extractor = build_atom_extractor(use_openrouter=True)
        # Should create hybrid extractor
        mock_hybrid_class.assert_called_once()
        assert extractor == mock_hybrid
    finally:
        # Clean up
        if "CKX_ATOM_REFINER_IMPL" in os.environ:
            del os.environ["CKX_ATOM_REFINER_IMPL"]


@patch("ck_exporter.bootstrap.make_openrouter_client")
@patch("ck_exporter.bootstrap.DspyAtomRefiner")
def test_build_atom_extractor_falls_back_on_dspy_import_error(mock_dspy_refiner_class, mock_make_client):
    """Test that build_atom_extractor falls back to OpenRouter if DSPy import fails."""
    mock_client = MagicMock()
    mock_make_client.return_value = mock_client

    # Make DSPy import fail
    mock_dspy_refiner_class.side_effect = ImportError("dspy-ai is not installed")

    os.environ["CKX_ATOM_REFINER_IMPL"] = "dspy"

    try:
        extractor = build_atom_extractor(use_openrouter=True)
        # Should fall back to OpenRouter
        assert extractor.__class__.__name__ == "OpenRouterAtomExtractor"
    finally:
        if "CKX_ATOM_REFINER_IMPL" in os.environ:
            del os.environ["CKX_ATOM_REFINER_IMPL"]


@patch("ck_exporter.bootstrap.make_openrouter_client")
def test_build_topic_labeler_defaults_to_openrouter(mock_make_client):
    """Test that build_topic_labeler defaults to OpenRouter when env var not set."""
    mock_client = MagicMock()
    mock_make_client.return_value = mock_client

    if "CKX_TOPIC_LABELER_IMPL" in os.environ:
        del os.environ["CKX_TOPIC_LABELER_IMPL"]

    labeler = build_topic_labeler(use_openrouter=True)

    assert labeler is not None
    assert hasattr(labeler, "label_topic")
    assert labeler.__class__.__name__ == "OpenRouterTopicLabeler"


@patch("ck_exporter.bootstrap.make_openrouter_client")
@patch("ck_exporter.bootstrap.DspyTopicLabeler")
def test_build_topic_labeler_uses_dspy_when_env_set(mock_dspy_labeler_class, mock_make_client):
    """Test that build_topic_labeler uses DSPy when CKX_TOPIC_LABELER_IMPL=dspy."""
    mock_dspy_labeler = MagicMock()
    mock_dspy_labeler_class.return_value = mock_dspy_labeler

    os.environ["CKX_TOPIC_LABELER_IMPL"] = "dspy"

    try:
        labeler = build_topic_labeler(use_openrouter=True)
        mock_dspy_labeler_class.assert_called_once_with(use_openrouter=True)
        assert labeler == mock_dspy_labeler
    finally:
        if "CKX_TOPIC_LABELER_IMPL" in os.environ:
            del os.environ["CKX_TOPIC_LABELER_IMPL"]


@patch("ck_exporter.bootstrap.make_openrouter_client")
@patch("ck_exporter.bootstrap.DspyTopicLabeler")
def test_build_topic_labeler_falls_back_on_dspy_import_error(mock_dspy_labeler_class, mock_make_client):
    """Test that build_topic_labeler falls back to OpenRouter if DSPy import fails."""
    mock_client = MagicMock()
    mock_make_client.return_value = mock_client

    # Make DSPy import fail
    mock_dspy_labeler_class.side_effect = ImportError("dspy-ai is not installed")

    os.environ["CKX_TOPIC_LABELER_IMPL"] = "dspy"

    try:
        labeler = build_topic_labeler(use_openrouter=True)
        # Should fall back to OpenRouter
        assert labeler.__class__.__name__ == "OpenRouterTopicLabeler"
    finally:
        if "CKX_TOPIC_LABELER_IMPL" in os.environ:
            del os.environ["CKX_TOPIC_LABELER_IMPL"]
