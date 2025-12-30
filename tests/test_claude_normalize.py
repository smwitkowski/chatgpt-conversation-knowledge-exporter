"""Tests for Claude conversation normalization."""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from ck_exporter.pipeline.io import (
    convert_claude_to_chatgpt,
    is_claude_conversation,
    load_conversations,
    parse_iso_timestamp,
)


def test_is_claude_conversation_valid():
    """Test detection of valid Claude conversation."""
    obj = {
        "platform": "CLAUDE_AI",
        "chat_messages": [],
        "uuid": "test-uuid",
    }
    assert is_claude_conversation(obj) is True


def test_is_claude_conversation_missing_platform():
    """Test detection fails when platform is missing or wrong."""
    obj = {
        "chat_messages": [],
        "uuid": "test-uuid",
    }
    assert is_claude_conversation(obj) is False

    obj2 = {
        "platform": "CHATGPT",
        "chat_messages": [],
    }
    assert is_claude_conversation(obj2) is False


def test_is_claude_conversation_missing_chat_messages():
    """Test detection fails when chat_messages is missing."""
    obj = {
        "platform": "CLAUDE_AI",
        "uuid": "test-uuid",
    }
    assert is_claude_conversation(obj) is False


def test_is_claude_conversation_not_dict():
    """Test detection fails for non-dict."""
    assert is_claude_conversation([]) is False
    assert is_claude_conversation("string") is False
    assert is_claude_conversation(None) is False


def test_parse_iso_timestamp_valid():
    """Test ISO timestamp parsing."""
    iso_str = "2025-12-18T18:06:43.449478+00:00"
    result = parse_iso_timestamp(iso_str)
    assert result is not None
    assert isinstance(result, float)
    assert result > 0


def test_parse_iso_timestamp_with_z():
    """Test ISO timestamp with Z suffix."""
    iso_str = "2025-12-18T18:06:43.449478Z"
    result = parse_iso_timestamp(iso_str)
    assert result is not None
    assert isinstance(result, float)


def test_parse_iso_timestamp_invalid():
    """Test invalid timestamp returns None."""
    assert parse_iso_timestamp("not-a-timestamp") is None
    assert parse_iso_timestamp("") is None
    assert parse_iso_timestamp(None) is None


def test_convert_claude_to_chatgpt_basic():
    """Test basic Claude conversion produces correct structure."""
    claude_conv = {
        "uuid": "claude-uuid-123",
        "name": "Test Claude Conversation",
        "project_uuid": "proj-uuid-999",
        "project": {"uuid": "proj-uuid-999", "name": "Test Project"},
        "chat_messages": [
            {
                "uuid": "msg-1",
                "sender": "human",
                "text": "Hello",
                "created_at": "2025-12-18T18:06:43.449478+00:00",
            },
            {
                "uuid": "msg-2",
                "sender": "assistant",
                "text": "Hi there",
                "created_at": "2025-12-18T18:06:44.449478+00:00",
            },
        ],
    }

    result = convert_claude_to_chatgpt(claude_conv)

    assert result["conversation_id"] == "claude-uuid-123"
    assert result["title"] == "Test Claude Conversation"
    assert result["project_id"] == "proj-uuid-999"
    assert result["project_name"] == "Test Project"
    assert result["current_node"] == "msg-2"
    assert "mapping" in result
    assert "msg-1" in result["mapping"]
    assert "msg-2" in result["mapping"]


def test_convert_claude_to_chatgpt_sender_mapping():
    """Test sender mapping: human→user, assistant→assistant, unknown→system."""
    claude_conv = {
        "uuid": "test",
        "chat_messages": [
            {"uuid": "msg-1", "sender": "human", "text": "Hello"},
            {"uuid": "msg-2", "sender": "assistant", "text": "Hi"},
            {"uuid": "msg-3", "sender": "unknown_type", "text": "System"},
        ],
    }

    result = convert_claude_to_chatgpt(claude_conv)

    assert result["mapping"]["msg-1"]["message"]["author"]["role"] == "user"
    assert result["mapping"]["msg-2"]["message"]["author"]["role"] == "assistant"
    assert result["mapping"]["msg-3"]["message"]["author"]["role"] == "system"


def test_convert_claude_to_chatgpt_parent_chain():
    """Test parent chain links sequentially."""
    claude_conv = {
        "uuid": "test",
        "chat_messages": [
            {"uuid": "msg-1", "sender": "human", "text": "First"},
            {"uuid": "msg-2", "sender": "assistant", "text": "Second"},
            {"uuid": "msg-3", "sender": "human", "text": "Third"},
        ],
    }

    result = convert_claude_to_chatgpt(claude_conv)

    # First message has no parent
    assert result["mapping"]["msg-1"]["parent"] is None
    # Second message points to first
    assert result["mapping"]["msg-2"]["parent"] == "msg-1"
    # Third message points to second
    assert result["mapping"]["msg-3"]["parent"] == "msg-2"
    # Current node is last
    assert result["current_node"] == "msg-3"


def test_convert_claude_to_chatgpt_timestamp_parsing():
    """Test created_at ISO parsing into create_time float."""
    claude_conv = {
        "uuid": "test",
        "chat_messages": [
            {
                "uuid": "msg-1",
                "sender": "human",
                "text": "Hello",
                "created_at": "2025-12-18T18:06:43.449478+00:00",
            },
        ],
    }

    result = convert_claude_to_chatgpt(claude_conv)

    create_time = result["mapping"]["msg-1"]["message"]["create_time"]
    assert create_time is not None
    assert isinstance(create_time, float)
    assert create_time > 0


def test_convert_claude_to_chatgpt_missing_timestamp():
    """Test missing created_at handled gracefully."""
    claude_conv = {
        "uuid": "test",
        "chat_messages": [
            {"uuid": "msg-1", "sender": "human", "text": "Hello"},
        ],
    }

    result = convert_claude_to_chatgpt(claude_conv)

    assert result["mapping"]["msg-1"]["message"]["create_time"] is None


def test_convert_claude_to_chatgpt_empty_messages():
    """Test empty chat_messages handled gracefully."""
    claude_conv = {
        "uuid": "test-uuid",
        "name": "Empty Conversation",
        "chat_messages": [],
    }

    result = convert_claude_to_chatgpt(claude_conv)

    assert result["conversation_id"] == "test-uuid"
    assert result["title"] == "Empty Conversation"
    assert result["mapping"] == {}
    assert result["current_node"] is None


def test_convert_claude_to_chatgpt_missing_name():
    """Test missing name uses fallback."""
    claude_conv = {
        "uuid": "test",
        "chat_messages": [{"uuid": "msg-1", "sender": "human", "text": "Hello"}],
    }

    result = convert_claude_to_chatgpt(claude_conv)

    assert result["title"] == "Untitled Conversation"


def test_load_conversations_claude():
    """Test load_conversations wraps Claude conversation in list."""
    claude_conv = {
        "platform": "CLAUDE_AI",
        "uuid": "claude-uuid",
        "name": "Test",
        "chat_messages": [
            {"uuid": "msg-1", "sender": "human", "text": "Hello"},
        ],
    }

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(claude_conv, f)
        temp_path = Path(f.name)

    try:
        result = load_conversations(temp_path)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["conversation_id"] == "claude-uuid"
        assert result[0]["title"] == "Test"
        assert "mapping" in result[0]
        assert "current_node" in result[0]
    finally:
        temp_path.unlink()


def test_load_conversations_claude_skips_missing_uuid():
    """Test messages without UUID are skipped."""
    claude_conv = {
        "platform": "CLAUDE_AI",
        "uuid": "test",
        "chat_messages": [
            {"uuid": "msg-1", "sender": "human", "text": "Hello"},
            {"sender": "assistant", "text": "No UUID"},  # Missing UUID
            {"uuid": "msg-3", "sender": "human", "text": "Third"},
        ],
    }

    result = convert_claude_to_chatgpt(claude_conv)

    # Should only have msg-1 and msg-3
    assert "msg-1" in result["mapping"]
    assert "msg-3" in result["mapping"]
    # msg-3 should point to msg-1 (skipping the one without UUID)
    assert result["mapping"]["msg-3"]["parent"] == "msg-1"
    assert result["current_node"] == "msg-3"

