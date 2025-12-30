"""Tests for input normalization."""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from tempfile import TemporaryDirectory

import pytest

from ck_exporter.pipeline.io import (
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


def test_load_conversations_directory_of_single_conversations():
    """Directory input should load many per-conversation JSON files."""
    conv_a = {
        "title": "A",
        "mapping": {"node-1": {"message": None, "parent": None}},
        "current_node": "node-1",
    }
    conv_b = {
        "title": "B",
        "mapping": {"node-2": {"message": None, "parent": None}},
        "current_node": "node-2",
    }

    with TemporaryDirectory() as d:
        dir_path = Path(d)
        a_path = dir_path / "chatgpt_a.json"
        b_path = dir_path / "chatgpt_b.json"
        a_path.write_text(json.dumps(conv_a), encoding="utf-8")
        b_path.write_text(json.dumps(conv_b), encoding="utf-8")

        result = load_conversations(dir_path)
        assert len(result) == 2

        ids = {r.get("conversation_id") or r.get("id") for r in result}
        assert ids == {"chatgpt_a", "chatgpt_b"}


def test_load_conversations_directory_limit_deterministic():
    """Directory input with limit should return first N files by sorted filename."""
    conv_a = {
        "title": "A",
        "mapping": {"node-1": {"message": None, "parent": None}},
        "current_node": "node-1",
    }
    conv_b = {
        "title": "B",
        "mapping": {"node-2": {"message": None, "parent": None}},
        "current_node": "node-2",
    }
    conv_c = {
        "title": "C",
        "mapping": {"node-3": {"message": None, "parent": None}},
        "current_node": "node-3",
    }

    with TemporaryDirectory() as d:
        dir_path = Path(d)
        # Create files in non-alphabetical order to test sorting
        z_path = dir_path / "z_conv.json"
        a_path = dir_path / "a_conv.json"
        m_path = dir_path / "m_conv.json"
        z_path.write_text(json.dumps(conv_c), encoding="utf-8")
        a_path.write_text(json.dumps(conv_a), encoding="utf-8")
        m_path.write_text(json.dumps(conv_b), encoding="utf-8")

        # Limit to 2 should return first 2 by sorted filename (a_conv, m_conv)
        result = load_conversations(dir_path, limit=2)
        assert len(result) == 2

        ids = {r.get("conversation_id") or r.get("id") for r in result}
        assert ids == {"a_conv", "m_conv"}  # Should be sorted alphabetically

        # Limit to 1 should return only first file
        result = load_conversations(dir_path, limit=1)
        assert len(result) == 1
        assert result[0].get("conversation_id") or result[0].get("id") == "a_conv"

        # Limit larger than available should return all
        result = load_conversations(dir_path, limit=10)
        assert len(result) == 3


def test_load_conversations_list_limit():
    """List input with limit should return first N conversations."""
    conversations = [
        {"id": "conv-1", "title": "First"},
        {"id": "conv-2", "title": "Second"},
        {"id": "conv-3", "title": "Third"},
        {"id": "conv-4", "title": "Fourth"},
    ]

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(conversations, f)
        temp_path = Path(f.name)

    try:
        # Limit to 2 should return first 2
        result = load_conversations(temp_path, limit=2)
        assert len(result) == 2
        assert result[0]["id"] == "conv-1"
        assert result[1]["id"] == "conv-2"

        # Limit to 1 should return first 1
        result = load_conversations(temp_path, limit=1)
        assert len(result) == 1
        assert result[0]["id"] == "conv-1"

        # Limit larger than available should return all
        result = load_conversations(temp_path, limit=10)
        assert len(result) == 4

        # No limit should return all
        result = load_conversations(temp_path)
        assert len(result) == 4
    finally:
        temp_path.unlink()


def test_load_conversations_single_file_limit():
    """Single file input with limit should still respect limit."""
    single_conv = {
        "title": "Test Conversation",
        "mapping": {"node-1": {"message": None, "parent": None}},
        "current_node": "node-1",
    }

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(single_conv, f)
        temp_path = Path(f.name)

    try:
        # Limit to 1 should return the conversation
        result = load_conversations(temp_path, limit=1)
        assert len(result) == 1

        # Limit to 0 should return empty list
        result = load_conversations(temp_path, limit=0)
        assert len(result) == 0

        # No limit should return the conversation
        result = load_conversations(temp_path)
        assert len(result) == 1
    finally:
        temp_path.unlink()


def test_load_conversations_md_file():
    """Test loading single Markdown meeting file returns 1 conversation."""
    md_content = """# Meeting Notes

## Summary

This is a summary.
"""

    with NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(md_content)
        temp_path = Path(f.name)

    try:
        result = load_conversations(temp_path)
        assert len(result) == 1
        assert "conversation_id" in result[0]
        assert result[0]["conversation_id"].startswith("meeting__")
        assert "mapping" in result[0]
        assert "current_node" in result[0]
        assert result[0]["title"] == "Meeting Notes"
    finally:
        temp_path.unlink()


def test_load_conversations_txt_file():
    """Test loading single text transcript file returns 1 conversation."""
    txt_content = """1:08 : Tanya Gastelum : Good afternoon.
1:09 : Scott Anderson : Hey, how are you?
"""

    with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(txt_content)
        temp_path = Path(f.name)

    try:
        result = load_conversations(temp_path)
        assert len(result) == 1
        assert "conversation_id" in result[0]
        assert result[0]["conversation_id"].startswith("meeting__")
        assert "mapping" in result[0]
        assert "current_node" in result[0]
        # Should have timestamp-based messages
        mapping = result[0]["mapping"]
        assert "00:01:08" in mapping
        assert "00:01:09" in mapping
    finally:
        temp_path.unlink()


