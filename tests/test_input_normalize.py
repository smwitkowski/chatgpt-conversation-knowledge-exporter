"""Tests for input normalization."""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from ck_exporter.input_normalize import (
    is_chatgpt_single_conversation,
    load_conversations,
)


def test_is_chatgpt_single_conversation_valid():
    """Test detection of valid ChatGPT single conversation."""
    obj = {
        "mapping": {},
        "current_node": "some-node",
        "title": "Test",
    }
    assert is_chatgpt_single_conversation(obj) is True


def test_is_chatgpt_single_conversation_missing_mapping():
    """Test detection fails when mapping is missing."""
    obj = {
        "current_node": "some-node",
        "title": "Test",
    }
    assert is_chatgpt_single_conversation(obj) is False


def test_is_chatgpt_single_conversation_missing_current_node():
    """Test detection fails when current_node is missing."""
    obj = {
        "mapping": {},
        "title": "Test",
    }
    assert is_chatgpt_single_conversation(obj) is False


def test_is_chatgpt_single_conversation_not_dict():
    """Test detection fails for non-dict."""
    assert is_chatgpt_single_conversation([]) is False
    assert is_chatgpt_single_conversation("string") is False
    assert is_chatgpt_single_conversation(None) is False


def test_load_conversations_list_passthrough():
    """Test list input returns list unchanged."""
    conversations = [
        {"id": "conv-1", "title": "First"},
        {"id": "conv-2", "title": "Second"},
    ]

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(conversations, f)
        temp_path = Path(f.name)

    try:
        result = load_conversations(temp_path)
        assert result == conversations
        assert len(result) == 2
    finally:
        temp_path.unlink()


def test_load_conversations_single_wraps():
    """Test single conversation dict wraps to 1-item list."""
    single_conv = {
        "title": "Test Conversation",
        "mapping": {
            "node-1": {
                "message": {
                    "id": "msg-1",
                    "author": {"role": "user"},
                    "content": {"parts": ["Hello"]},
                },
                "parent": None,
            }
        },
        "current_node": "node-1",
    }

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(single_conv, f)
        temp_path = Path(f.name)

    try:
        result = load_conversations(temp_path)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["title"] == "Test Conversation"
        assert result[0]["mapping"] == single_conv["mapping"]
    finally:
        temp_path.unlink()


def test_load_conversations_id_injection():
    """Test conversation_id injection from filename when missing."""
    single_conv = {
        "title": "Test Conversation",
        "mapping": {
            "node-1": {
                "message": {
                    "id": "msg-1",
                    "author": {"role": "user"},
                    "content": {"parts": ["Hello"]},
                },
                "parent": None,
            }
        },
        "current_node": "node-1",
        # No id or conversation_id
    }

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(single_conv, f)
        temp_path = Path(f.name)

    try:
        result = load_conversations(temp_path)
        assert len(result) == 1
        # Should have conversation_id injected from filename stem
        assert result[0]["conversation_id"] == temp_path.stem
    finally:
        temp_path.unlink()


def test_load_conversations_id_preserved():
    """Test existing id/conversation_id is preserved."""
    single_conv = {
        "id": "existing-id",
        "title": "Test Conversation",
        "mapping": {"node-1": {"message": None, "parent": None}},
        "current_node": "node-1",
    }

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(single_conv, f)
        temp_path = Path(f.name)

    try:
        result = load_conversations(temp_path)
        assert len(result) == 1
        assert result[0]["id"] == "existing-id"
        # Should not inject conversation_id if id exists
        assert "conversation_id" not in result[0] or result[0].get("conversation_id") != temp_path.stem
    finally:
        temp_path.unlink()


def test_load_conversations_conversation_id_preserved():
    """Test existing conversation_id is preserved."""
    single_conv = {
        "conversation_id": "existing-conv-id",
        "title": "Test Conversation",
        "mapping": {"node-1": {"message": None, "parent": None}},
        "current_node": "node-1",
    }

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(single_conv, f)
        temp_path = Path(f.name)

    try:
        result = load_conversations(temp_path)
        assert len(result) == 1
        assert result[0]["conversation_id"] == "existing-conv-id"
    finally:
        temp_path.unlink()


def test_load_conversations_unsupported_format():
    """Test unsupported format raises helpful error."""
    unsupported = {
        "some": "data",
        "but": "no mapping or current_node",
    }

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(unsupported, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError) as exc_info:
            load_conversations(temp_path)
        assert "Unsupported input format" in str(exc_info.value)
        assert "list of conversations" in str(exc_info.value)
        assert "mapping" in str(exc_info.value)
        assert "current_node" in str(exc_info.value)
    finally:
        temp_path.unlink()


def test_load_conversations_invalid_json():
    """Test invalid JSON raises appropriate error."""
    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("{ invalid json }")
        temp_path = Path(f.name)

    try:
        with pytest.raises(json.JSONDecodeError):
            load_conversations(temp_path)
    finally:
        temp_path.unlink()

