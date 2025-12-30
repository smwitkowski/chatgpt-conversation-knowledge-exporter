"""Tests for meeting notes parsing and normalization."""

import hashlib
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest

from ck_exporter.pipeline.io.meeting_notes import (
    generate_document_id,
    is_meeting_artifact,
    normalize_timestamp,
    parse_markdown_meeting,
    parse_text_transcript,
)


def test_normalize_timestamp_mss():
    """Test normalization of M:SS format."""
    assert normalize_timestamp("1:08") == "00:01:08"
    assert normalize_timestamp("59:59") == "00:59:59"
    assert normalize_timestamp("0:30") == "00:00:30"


def test_normalize_timestamp_hmmss():
    """Test normalization of H:MM:SS format."""
    assert normalize_timestamp("1:02:15") == "01:02:15"
    assert normalize_timestamp("0:00:05") == "00:00:05"
    assert normalize_timestamp("12:34:56") == "12:34:56"


def test_normalize_timestamp_overflow():
    """Test that minutes >= 60 are carried into hours."""
    assert normalize_timestamp("62:15") == "01:02:15"
    assert normalize_timestamp("125:30") == "02:05:30"
    assert normalize_timestamp("90:00") == "01:30:00"


def test_normalize_timestamp_with_anchor():
    """Test normalization removes anchor link syntax."""
    assert normalize_timestamp("00:03:03 {#00:03:03}") == "00:03:03"
    assert normalize_timestamp("1:08 {#anchor}") == "00:01:08"


def test_normalize_timestamp_invalid():
    """Test invalid timestamp formats return default."""
    assert normalize_timestamp("") == "00:00:00"
    assert normalize_timestamp("invalid") == "00:00:00"
    assert normalize_timestamp("abc:def") == "00:00:00"


def test_generate_document_id_stable():
    """Test that same content generates same ID."""
    path = Path("test_meeting.md")
    content1 = b"Test meeting content"
    content2 = b"Test meeting content"

    id1 = generate_document_id(path, content1)
    id2 = generate_document_id(path, content2)

    assert id1 == id2
    assert id1.startswith("meeting__")
    assert "test_meeting" in id1  # Slug uses underscores, not hyphens


def test_generate_document_id_changes():
    """Test that different content generates different ID."""
    path = Path("test_meeting.md")
    content1 = b"Test meeting content"
    content2 = b"Different meeting content"

    id1 = generate_document_id(path, content1)
    id2 = generate_document_id(path, content2)

    assert id1 != id2
    assert id1.startswith("meeting__")
    assert id2.startswith("meeting__")


def test_generate_document_id_slug():
    """Test that filename is properly slugified."""
    path = Path("My Meeting Notes 2025.md")
    content = b"content"

    doc_id = generate_document_id(path, content)

    assert "my-meeting-notes-2025" in doc_id
    assert doc_id.startswith("meeting__")


def test_is_meeting_artifact():
    """Test detection of meeting artifact files."""
    assert is_meeting_artifact(Path("test.md")) is True
    assert is_meeting_artifact(Path("test.txt")) is True
    assert is_meeting_artifact(Path("test.MD")) is True
    assert is_meeting_artifact(Path("test.TXT")) is True
    assert is_meeting_artifact(Path("test.json")) is False
    assert is_meeting_artifact(Path("test.py")) is False


def test_parse_markdown_meet_notes():
    """Test parsing Markdown meeting notes creates notes messages."""
    content = """# Meeting Notes

## Summary

This is a summary of the meeting.

### Details

Some details here.
"""

    with NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        result = parse_markdown_meeting(temp_path)

        assert "conversation_id" in result
        assert result["title"] == "Meeting Notes"
        assert "mapping" in result
        assert "current_node" in result

        # Should have notes messages
        mapping = result["mapping"]
        assert any("notes:" in node_id for node_id in mapping.keys())
    finally:
        temp_path.unlink()


def test_parse_markdown_transcript_timestamps():
    """Test parsing Markdown transcript with timestamps."""
    content = """# Meeting Transcript

### 00:00:00 {#00:00:00}

**Speaker 1:** Hello

### 00:03:03 {#00:03:03}

**Speaker 2:** Hi there
"""

    with NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        result = parse_markdown_meeting(temp_path)

        mapping = result["mapping"]
        # Should have timestamp-based message IDs
        assert "00:00:00" in mapping
        assert "00:03:03" in mapping

        # Check message content
        msg1 = mapping["00:00:00"]["message"]
        assert "Hello" in msg1["content"]["parts"][0]
    finally:
        temp_path.unlink()


def test_parse_markdown_action_items():
    """Test that action items section gets prefixed hint."""
    content = """# Meeting Notes

### Suggested next steps

- [ ] Task 1
- [ ] Task 2
"""

    with NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        result = parse_markdown_meeting(temp_path)

        mapping = result["mapping"]
        # Find the action items message (slugified heading becomes "suggested-next-steps")
        action_msg = None
        for node_id, node in mapping.items():
            if "suggested-next-steps" in node_id or "next-steps" in node_id or "action" in node_id.lower():
                action_msg = node["message"]
                break

        assert action_msg is not None, f"Action items message not found. Available node_ids: {list(mapping.keys())}"
        content_text = action_msg["content"]["parts"][0]
        assert "Action items (treat as commitments/tasks):" in content_text
        assert "Task 1" in content_text
    finally:
        temp_path.unlink()


def test_parse_text_transcript_teams():
    """Test parsing Teams-style text transcript."""
    content = """1:08 : Tanya Gastelum : Good, good afternoon.
1:09 : Scott Anderson : Hey, how are you?
1:11 : Tanya Gastelum : Yeah, I'm good. How about you?
"""

    with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        result = parse_text_transcript(temp_path)

        assert "conversation_id" in result
        assert result["title"] == temp_path.stem
        assert "mapping" in result
        assert "current_node" in result

        mapping = result["mapping"]
        # Should have normalized timestamp IDs
        assert "00:01:08" in mapping
        assert "00:01:09" in mapping
        assert "00:01:11" in mapping

        # Check message content
        msg1 = mapping["00:01:08"]["message"]
        assert "**Tanya Gastelum:**" in msg1["content"]["parts"][0]
        assert "Good, good afternoon" in msg1["content"]["parts"][0]
    finally:
        temp_path.unlink()


def test_parse_text_transcript_continuation():
    """Test that non-matching lines attach to previous message."""
    content = """1:08 : Tanya Gastelum : First line
This is a continuation line
1:09 : Scott Anderson : Second message
"""

    with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        result = parse_text_transcript(temp_path)

        mapping = result["mapping"]
        msg1 = mapping["00:01:08"]["message"]
        content_text = msg1["content"]["parts"][0]

        # Continuation should be appended
        assert "First line" in content_text
        assert "continuation line" in content_text
    finally:
        temp_path.unlink()


def test_parse_text_transcript_empty():
    """Test parsing empty transcript creates fallback message."""
    content = ""

    with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        result = parse_text_transcript(temp_path)

        mapping = result["mapping"]
        # Should have a fallback notes message
        assert "notes:transcript" in mapping or len(mapping) > 0
    finally:
        temp_path.unlink()


def test_load_conversations_mixed_directory():
    """Test loading from directory with mixed .md and .txt files."""
    from ck_exporter.pipeline.io import load_conversations

    md_content = """# Meeting 1

## Summary

First meeting notes.
"""

    txt_content = """1:08 : Speaker : First transcript line
"""

    with TemporaryDirectory() as d:
        dir_path = Path(d)
        md_path = dir_path / "meeting1.md"
        txt_path = dir_path / "meeting2.txt"

        md_path.write_text(md_content, encoding="utf-8")
        txt_path.write_text(txt_content, encoding="utf-8")

        result = load_conversations(dir_path)

        assert len(result) == 2
        # Both should have conversation_id
        assert all("conversation_id" in conv for conv in result)
        # Both should have mapping/current_node structure
        assert all("mapping" in conv for conv in result)
        assert all("current_node" in conv for conv in result)

