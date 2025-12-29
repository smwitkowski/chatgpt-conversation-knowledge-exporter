"""Tests for chunking utilities."""

import pytest

from ck_exporter.chunking import chunk_messages, chunk_text, estimate_tokens


def test_estimate_tokens():
    """Test token estimation."""
    text = "Hello, this is a test message."
    tokens = estimate_tokens(text)
    assert tokens > 0
    assert isinstance(tokens, int)


def test_chunk_text_small():
    """Test chunking small text."""
    text = "This is a short text."
    chunks = chunk_text(text, max_tokens=100)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_large():
    """Test chunking large text."""
    text = ". ".join([f"Sentence {i}" for i in range(100)])
    chunks = chunk_text(text, max_tokens=50)
    assert len(chunks) > 1


def test_chunk_messages():
    """Test chunking message list."""
    messages = [
        {"role": "user", "text": "Message 1", "id": "1"},
        {"role": "assistant", "text": "Response 1", "id": "2"},
        {"role": "user", "text": "Message 2", "id": "3"},
    ]

    chunks = chunk_messages(messages, max_tokens=1000)
    assert len(chunks) >= 1
    assert all(isinstance(chunk, list) for chunk in chunks)
    assert all(len(chunk) > 0 for chunk in chunks)


def test_chunk_empty():
    """Test chunking empty input."""
    assert chunk_text("") == []
    assert chunk_messages([]) == []
