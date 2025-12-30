"""Tests for linearization."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from ck_exporter.linearize import linearize_conversation, linearize_export, write_conversation_markdown


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


def test_linearize_export_single_conversation():
    """Test linearize_export works with single conversation file (no id)."""
    single_conv = {
        "title": "Single Test Conversation",
        "current_node": "msg-2",
        "mapping": {
            "msg-1": {
                "message": {
                    "id": "msg-1",
                    "author": {"role": "user"},
                    "content": {"parts": ["First message"]},
                    "create_time": 1609459200.0,
                },
                "parent": None,
            },
            "msg-2": {
                "message": {
                    "id": "msg-2",
                    "author": {"role": "assistant"},
                    "content": {"parts": ["Response"]},
                    "create_time": 1609459260.0,
                },
                "parent": "msg-1",
            },
        },
        # No id or conversation_id - should be injected from filename
    }

    with TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        input_file = tmp_path / "test_single_conv.json"
        output_dir = tmp_path / "output"

        # Write single conversation JSON
        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(single_conv, f)

        # Run linearize_export
        linearize_export(input_file, output_dir)

        # Verify output was created with filename-based ID
        expected_conv_id = "test_single_conv"
        output_path = output_dir / expected_conv_id / "conversation.md"

        assert output_path.exists()
        content = output_path.read_text(encoding="utf-8")

        assert "Single Test Conversation" in content
        assert expected_conv_id in content
        assert "First message" in content
        assert "Response" in content


def test_linearize_export_claude_conversation():
    """Test linearize_export works with Claude conversation file."""
    claude_conv = {
        "platform": "CLAUDE_AI",
        "uuid": "claude-test-uuid-123",
        "name": "Claude Test Conversation",
        "chat_messages": [
            {
                "uuid": "msg-1",
                "sender": "human",
                "text": "Hello from Claude",
                "created_at": "2025-12-18T18:06:43.449478+00:00",
            },
            {
                "uuid": "msg-2",
                "sender": "assistant",
                "text": "Hi, how can I help?",
                "created_at": "2025-12-18T18:06:44.449478+00:00",
            },
        ],
    }

    with TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        input_file = tmp_path / "test_claude_conv.json"
        output_dir = tmp_path / "output"

        # Write Claude conversation JSON
        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(claude_conv, f)

        # Run linearize_export
        linearize_export(input_file, output_dir)

        # Verify output was created with Claude UUID as conversation ID
        expected_conv_id = "claude-test-uuid-123"
        output_path = output_dir / expected_conv_id / "conversation.md"

        assert output_path.exists()
        content = output_path.read_text(encoding="utf-8")

        assert "Claude Test Conversation" in content
        assert expected_conv_id in content
        assert "Hello from Claude" in content
        assert "Hi, how can I help?" in content
