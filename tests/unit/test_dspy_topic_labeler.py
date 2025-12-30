"""Unit tests for DSPy topic labeler adapter."""

from unittest.mock import MagicMock, patch

import pytest

from ck_exporter.adapters.dspy_topic_labeler import DspyTopicLabeler


@pytest.fixture
def mock_dspy_lm():
    """Create a mock DSPy LM."""
    mock_lm = MagicMock()
    return mock_lm


@pytest.fixture
def mock_dspy_program():
    """Create a mock DSPy program that returns deterministic outputs."""
    mock_program = MagicMock()
    mock_program.return_value = {
        "name": "Test Topic Name",
        "description": "This is a test topic description.",
    }
    return mock_program


@patch("ck_exporter.adapters.dspy_topic_labeler.create_label_topic_program")
@patch("ck_exporter.adapters.dspy_topic_labeler.get_dspy_lm_for_labeling")
def test_dspy_topic_labeler_success(mock_get_lm, mock_create_program, mock_dspy_lm, mock_dspy_program):
    """Test successful topic labeling with DSPy."""
    mock_get_lm.return_value = mock_dspy_lm
    mock_create_program.return_value = mock_dspy_program

    labeler = DspyTopicLabeler(use_openrouter=True, lm=mock_dspy_lm)
    labeler.program = mock_dspy_program

    representative_docs = [
        ("conv-1", "This is a test conversation about testing."),
        ("conv-2", "Another conversation about testing and quality assurance."),
    ]
    keywords = ["testing", "qa", "quality"]

    result = labeler.label_topic(topic_id=1, representative_docs=representative_docs, keywords=keywords)

    assert result["name"] == "Test Topic Name"
    assert result["description"] == "This is a test topic description."
    mock_dspy_program.assert_called_once()


@patch("ck_exporter.adapters.dspy_topic_labeler.create_label_topic_program")
@patch("ck_exporter.adapters.dspy_topic_labeler.get_dspy_lm_for_labeling")
def test_dspy_topic_labeler_fallback_on_error(mock_get_lm, mock_create_program, mock_dspy_lm):
    """Test that labeler falls back to default values on error."""
    mock_get_lm.return_value = mock_dspy_lm
    mock_program = MagicMock()
    mock_program.side_effect = Exception("DSPy error")
    mock_create_program.return_value = mock_program

    labeler = DspyTopicLabeler(use_openrouter=True, lm=mock_dspy_lm)
    labeler.program = mock_program

    representative_docs = [("conv-1", "Test")]
    keywords = ["test"]

    result = labeler.label_topic(topic_id=1, representative_docs=representative_docs, keywords=keywords)

    assert result["name"] == "Topic 1"
    assert result["description"] == "No description available"


@patch("ck_exporter.adapters.dspy_topic_labeler.create_label_topic_program")
@patch("ck_exporter.adapters.dspy_topic_labeler.get_dspy_lm_for_labeling")
def test_dspy_topic_labeler_empty_name_fallback(mock_get_lm, mock_create_program, mock_dspy_lm):
    """Test that empty name falls back to default."""
    mock_get_lm.return_value = mock_dspy_lm
    mock_program = MagicMock()
    mock_program.return_value = {"name": "", "description": "Valid description"}
    mock_create_program.return_value = mock_program

    labeler = DspyTopicLabeler(use_openrouter=True, lm=mock_dspy_lm)
    labeler.program = mock_program

    result = labeler.label_topic(topic_id=2, representative_docs=[], keywords=[])

    assert result["name"] == "Topic 2"
    assert result["description"] == "Valid description"


def test_dspy_topic_labeler_import_error():
    """Test that ImportError is raised when dspy-ai is not installed."""
    with patch("ck_exporter.adapters.dspy_topic_labeler.dspy", None):
        with pytest.raises(ImportError, match="dspy-ai is not installed"):
            DspyTopicLabeler(use_openrouter=True)
