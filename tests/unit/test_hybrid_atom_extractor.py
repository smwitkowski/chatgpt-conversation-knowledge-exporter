"""Unit tests for hybrid atom extractor."""

from unittest.mock import MagicMock

import pytest

from ck_exporter.adapters.dspy_atom_refiner import DspyAtomRefiner
from ck_exporter.adapters.hybrid_atom_extractor import HybridAtomExtractor
from ck_exporter.adapters.openrouter_atom_extractor import OpenRouterAtomExtractor


@pytest.fixture
def mock_openrouter_extractor():
    """Create a mock OpenRouter extractor."""
    extractor = MagicMock(spec=OpenRouterAtomExtractor)
    extractor.extract_from_chunk.return_value = {
        "facts": [{"type": "fact", "statement": "Test"}],
        "decisions": [],
        "open_questions": [],
    }
    return extractor


@pytest.fixture
def mock_dspy_refiner():
    """Create a mock DSPy refiner."""
    refiner = MagicMock(spec=DspyAtomRefiner)
    refiner.refine_atoms.return_value = {
        "facts": [{"type": "fact", "statement": "Refined test"}],
        "decisions": [],
        "open_questions": [],
    }
    return refiner


def test_hybrid_extractor_delegates_pass1(mock_openrouter_extractor, mock_dspy_refiner):
    """Test that Pass 1 delegates to OpenRouter extractor."""
    extractor = HybridAtomExtractor(
        openrouter_extractor=mock_openrouter_extractor,
        dspy_refiner=mock_dspy_refiner,
    )

    result = extractor.extract_from_chunk("test chunk text")

    mock_openrouter_extractor.extract_from_chunk.assert_called_once_with("test chunk text")
    assert result == mock_openrouter_extractor.extract_from_chunk.return_value


def test_hybrid_extractor_delegates_pass2(mock_openrouter_extractor, mock_dspy_refiner):
    """Test that Pass 2 delegates to DSPy refiner."""
    extractor = HybridAtomExtractor(
        openrouter_extractor=mock_openrouter_extractor,
        dspy_refiner=mock_dspy_refiner,
    )

    candidates = {"facts": [], "decisions": [], "open_questions": []}
    result = extractor.refine_atoms(candidates, "conv-1", "Test Title")

    mock_dspy_refiner.refine_atoms.assert_called_once_with(candidates, "conv-1", "Test Title")
    assert result == mock_dspy_refiner.refine_atoms.return_value
