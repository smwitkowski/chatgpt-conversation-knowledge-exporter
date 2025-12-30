"""Unit tests for DSPy atom refiner adapter."""

import json
from unittest.mock import MagicMock, patch

import pytest

from ck_exporter.adapters.dspy_atom_refiner import DspyAtomRefiner


@pytest.fixture
def sample_candidates():
    """Sample candidate atoms for testing."""
    return {
        "facts": [
            {"type": "fact", "topic": "testing", "statement": "Test fact 1", "status": "active"},
            {"type": "fact", "topic": "testing", "statement": "Test fact 2", "status": "active"},
        ],
        "decisions": [
            {
                "type": "decision",
                "topic": "architecture",
                "statement": "Use Python",
                "status": "active",
                "alternatives": ["Java", "Go"],
            }
        ],
        "open_questions": [{"question": "What about performance?", "topic": "architecture"}],
    }


@pytest.fixture
def mock_dspy_program():
    """Create a mock DSPy program that returns valid JSON."""
    mock_program = MagicMock()
    refined_facts = [{"type": "fact", "topic": "testing", "statement": "Test fact (merged)", "status": "active"}]
    refined_decisions = [
        {
            "type": "decision",
            "topic": "architecture",
            "statement": "Use Python",
            "status": "active",
            "alternatives": ["Java", "Go"],
        }
    ]
    refined_questions = [{"question": "What about performance?", "topic": "architecture"}]

    mock_program.return_value = {
        "facts_json": json.dumps(refined_facts),
        "decisions_json": json.dumps(refined_decisions),
        "open_questions_json": json.dumps(refined_questions),
    }
    return mock_program


@patch("ck_exporter.adapters.dspy_atom_refiner.create_refine_atoms_program")
@patch("ck_exporter.adapters.dspy_atom_refiner.get_dspy_lm_for_refinement")
def test_dspy_atom_refiner_success(mock_get_lm, mock_create_program, mock_dspy_lm, sample_candidates, mock_dspy_program):
    """Test successful atom refinement with DSPy."""
    mock_get_lm.return_value = mock_dspy_lm
    mock_create_program.return_value = mock_dspy_program

    refiner = DspyAtomRefiner(use_openrouter=True, lm=mock_dspy_lm)
    refiner.program = mock_dspy_program

    result = refiner.refine_atoms(
        all_candidates=sample_candidates,
        conversation_id="test-conv-1",
        conversation_title="Test Conversation",
    )

    assert "facts" in result
    assert "decisions" in result
    assert "open_questions" in result
    assert isinstance(result["facts"], list)
    assert isinstance(result["decisions"], list)
    assert isinstance(result["open_questions"], list)
    mock_dspy_program.assert_called_once()


@patch("ck_exporter.adapters.dspy_atom_refiner.create_refine_atoms_program")
@patch("ck_exporter.adapters.dspy_atom_refiner.get_dspy_lm_for_refinement")
def test_dspy_atom_refiner_invalid_json_fallback(mock_get_lm, mock_create_program, mock_dspy_lm, sample_candidates):
    """Test that refiner falls back to candidates on invalid JSON."""
    mock_get_lm.return_value = mock_dspy_lm
    mock_program = MagicMock()
    mock_program.return_value = {
        "facts_json": "not valid json",
        "decisions_json": "[]",
        "open_questions_json": "[]",
    }
    mock_create_program.return_value = mock_program

    refiner = DspyAtomRefiner(use_openrouter=True, lm=mock_dspy_lm)
    refiner.program = mock_program

    result = refiner.refine_atoms(
        all_candidates=sample_candidates,
        conversation_id="test-conv-1",
        conversation_title="Test",
    )

    # Should return original candidates due to JSON parse error
    assert result == sample_candidates


@patch("ck_exporter.adapters.dspy_atom_refiner.create_refine_atoms_program")
@patch("ck_exporter.adapters.dspy_atom_refiner.get_dspy_lm_for_refinement")
def test_dspy_atom_refiner_non_list_fallback(mock_get_lm, mock_create_program, mock_dspy_lm, sample_candidates):
    """Test that refiner falls back when DSPy returns non-list."""
    mock_get_lm.return_value = mock_dspy_lm
    mock_program = MagicMock()
    mock_program.return_value = {
        "facts_json": '{"not": "a list"}',
        "decisions_json": "[]",
        "open_questions_json": "[]",
    }
    mock_create_program.return_value = mock_program

    refiner = DspyAtomRefiner(use_openrouter=True, lm=mock_dspy_lm)
    refiner.program = mock_program

    result = refiner.refine_atoms(
        all_candidates=sample_candidates,
        conversation_id="test-conv-1",
        conversation_title="Test",
    )

    # Should return original candidates due to non-list facts
    assert result == sample_candidates


@patch("ck_exporter.adapters.dspy_atom_refiner.create_refine_atoms_program")
@patch("ck_exporter.adapters.dspy_atom_refiner.get_dspy_lm_for_refinement")
def test_dspy_atom_refiner_exception_fallback(mock_get_lm, mock_create_program, mock_dspy_lm, sample_candidates):
    """Test that refiner falls back on exception."""
    mock_get_lm.return_value = mock_dspy_lm
    mock_program = MagicMock()
    mock_program.side_effect = Exception("DSPy error")
    mock_create_program.return_value = mock_program

    refiner = DspyAtomRefiner(use_openrouter=True, lm=mock_dspy_lm)
    refiner.program = mock_program

    result = refiner.refine_atoms(
        all_candidates=sample_candidates,
        conversation_id="test-conv-1",
        conversation_title="Test",
    )

    # Should return original candidates on exception
    assert result == sample_candidates


def test_dspy_atom_refiner_import_error():
    """Test that ImportError is raised when dspy-ai is not installed."""
    with patch("ck_exporter.adapters.dspy_atom_refiner.dspy", None):
        with pytest.raises(ImportError, match="dspy-ai is not installed"):
            DspyAtomRefiner(use_openrouter=True)
