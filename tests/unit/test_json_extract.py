"""Unit tests for JSON extraction utilities."""

import json

import pytest

from ck_exporter.programs.json_extract import extract_json_from_text


def test_extract_raw_json():
    """Test parsing raw JSON."""
    data = {"facts": [{"type": "fact", "statement": "test"}], "decisions": []}
    text = json.dumps(data)
    result = extract_json_from_text(text)
    assert result == data


def test_extract_json_from_markdown_code_block():
    """Test parsing JSON from markdown code block."""
    data = {"facts": [{"type": "fact", "statement": "test"}], "decisions": []}
    text = f"```json\n{json.dumps(data)}\n```"
    result = extract_json_from_text(text)
    assert result == data


def test_extract_json_from_code_block_no_lang():
    """Test parsing JSON from code block without language."""
    data = {"facts": [{"type": "fact", "statement": "test"}], "decisions": []}
    text = f"```\n{json.dumps(data)}\n```"
    result = extract_json_from_text(text)
    assert result == data


def test_extract_json_rejects_garbage():
    """Test that garbage text returns None."""
    result = extract_json_from_text("This is not JSON at all!")
    assert result is None


def test_extract_json_handles_malformed():
    """Test that malformed JSON returns None."""
    result = extract_json_from_text('{"facts": [unclosed}')
    assert result is None


def test_extract_json_strips_whitespace():
    """Test that whitespace is stripped."""
    data = {"facts": []}
    text = f"   \n{json.dumps(data)}\n   "
    result = extract_json_from_text(text)
    assert result == data
