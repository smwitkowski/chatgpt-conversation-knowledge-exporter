"""Tests for linearization."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from ck_exporter.linearize import linearize_conversation, write_conversation_markdown


@pytest.fixture
def sample_conversation():
    """Create a minimal sample conversation."""
    return {
        "id": "test-conv-123",
        "title": "Test Conversation",
        "current_node": "msg-3",
        "mapping": {
            "msg-1": {
                "message": {
                    "id": "msg-1",
                    "author": {"role": "user"},
                    "content": {"parts": ["Hello, this is a test message."]},
                    "create_time": 1609459200.0,  # 2021-01-01 00:00:00
                },
                "parent": None,
            },
            "msg-2": {
                "message": {
                    "id": "msg-2",
                    "author": {"role": "assistant"},
                    "content": {"parts": ["This is a response."]},
                    "create_time": 1609459260.0,
                },
                "parent": "msg-1",
            },
            "msg-3": {
                "message": {
                    "id": "msg-3",
                    "author": {"role": "user"},
                    "content": {"parts": ["Another message."]},
                    "create_time": 1609459320.0,
                },
                "parent": "msg-2",
            },
        },
    }


def test_linearize_conversation(sample_conversation):
    """Test linearization produces correct order."""
    messages = linearize_conversation(sample_conversation)

    assert len(messages) == 3
    assert messages[0]["role"] == "user"
    assert messages[0]["id"] == "msg-1"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["id"] == "msg-2"
    assert messages[2]["role"] == "user"
    assert messages[2]["id"] == "msg-3"


def test_write_conversation_markdown(sample_conversation):
    """Test markdown output generation."""
    messages = linearize_conversation(sample_conversation)

    with TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        output_path = write_conversation_markdown(
            messages,
            "test-conv-123",
            "Test Conversation",
            output_dir,
        )

        assert output_path.exists()
        content = output_path.read_text(encoding="utf-8")

        assert "Test Conversation" in content
        assert "test-conv-123" in content
        assert "Hello, this is a test message" in content
        assert "This is a response" in content
        assert "Another message" in content


def test_linearize_empty_conversation():
    """Test handling of conversation without current_node."""
    conv = {"id": "empty", "mapping": {}}
    messages = linearize_conversation(conv)
    assert messages == []


def test_linearize_missing_parts():
    """Test handling of messages with missing content."""
    conv = {
        "id": "test",
        "current_node": "msg-1",
        "mapping": {
            "msg-1": {
                "message": {
                    "id": "msg-1",
                    "author": {"role": "user"},
                    "content": {},  # No parts
                    "create_time": 1609459200.0,
                },
                "parent": None,
            },
        },
    }
    messages = linearize_conversation(conv)
    assert len(messages) == 0
