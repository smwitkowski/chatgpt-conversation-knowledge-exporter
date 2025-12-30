"""Tests for topic discovery module."""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest

from ck_exporter.topic_discovery import build_conversation_documents


def test_build_conversation_documents_basic():
    """Test building documents from atoms, decisions, and questions."""
    with TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create input conversation JSON
        conversations = [
            {
                "conversation_id": "conv-1",
                "title": "Test Conversation 1",
                "mapping": {},
                "current_node": None,
            }
        ]
        input_json = tmp_path / "conversations.json"
        with input_json.open("w") as f:
            json.dump(conversations, f)

        # Create consolidated atoms
        atoms_path = tmp_path / "atoms.jsonl"
        with atoms_path.open("w") as f:
            f.write(
                json.dumps(
                    {
                        "type": "fact",
                        "topic": "architecture",
                        "statement": "System uses PostgreSQL",
                        "source_conversation_id": "conv-1",
                    }
                )
                + "\n"
            )

        # Create consolidated decisions
        decisions_path = tmp_path / "decisions.jsonl"
        with decisions_path.open("w") as f:
            f.write(
                json.dumps(
                    {
                        "type": "decision",
                        "topic": "architecture",
                        "statement": "Use PostgreSQL for storage",
                        "source_conversation_id": "conv-1",
                    }
                )
                + "\n"
            )

        # Create consolidated questions
        questions_path = tmp_path / "open_questions.jsonl"
        with questions_path.open("w") as f:
            f.write(
                json.dumps(
                    {
                        "question": "What database to use?",
                        "topic": "architecture",
                        "source_conversation_id": "conv-1",
                    }
                )
                + "\n"
            )

        # Build documents
        docs, titles = build_conversation_documents(
            input_json, atoms_path, decisions_path, questions_path
        )

        assert "conv-1" in docs
        assert "conv-1" in titles
        assert titles["conv-1"] == "Test Conversation 1"

        doc_text = docs["conv-1"]
        assert "Test Conversation 1" in doc_text
        assert "System uses PostgreSQL" in doc_text
        assert "Use PostgreSQL for storage" in doc_text
        assert "What database to use?" in doc_text


def test_build_conversation_documents_multiple_conversations():
    """Test building documents for multiple conversations."""
    with TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        conversations = [
            {
                "conversation_id": "conv-1",
                "title": "Conversation 1",
                "mapping": {},
                "current_node": None,
            },
            {
                "conversation_id": "conv-2",
                "title": "Conversation 2",
                "mapping": {},
                "current_node": None,
            },
        ]
        input_json = tmp_path / "conversations.json"
        with input_json.open("w") as f:
            json.dump(conversations, f)

        atoms_path = tmp_path / "atoms.jsonl"
        with atoms_path.open("w") as f:
            f.write(
                json.dumps(
                    {
                        "type": "fact",
                        "statement": "Fact 1",
                        "source_conversation_id": "conv-1",
                    }
                )
                + "\n"
            )
            f.write(
                json.dumps(
                    {
                        "type": "fact",
                        "statement": "Fact 2",
                        "source_conversation_id": "conv-2",
                    }
                )
                + "\n"
            )

        decisions_path = tmp_path / "decisions.jsonl"
        with decisions_path.open("w") as f:
            pass  # Empty

        questions_path = tmp_path / "open_questions.jsonl"
        with questions_path.open("w") as f:
            pass  # Empty

        docs, titles = build_conversation_documents(
            input_json, atoms_path, decisions_path, questions_path
        )

        assert len(docs) == 2
        assert "conv-1" in docs
        assert "conv-2" in docs
        assert "Fact 1" in docs["conv-1"]
        assert "Fact 2" in docs["conv-2"]


def test_build_conversation_documents_empty_artifacts():
    """Test building documents when artifacts are empty."""
    with TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        conversations = [
            {
                "conversation_id": "conv-1",
                "title": "Empty Conversation",
                "mapping": {},
                "current_node": None,
            }
        ]
        input_json = tmp_path / "conversations.json"
        with input_json.open("w") as f:
            json.dump(conversations, f)

        atoms_path = tmp_path / "atoms.jsonl"
        atoms_path.touch()

        decisions_path = tmp_path / "decisions.jsonl"
        decisions_path.touch()

        questions_path = tmp_path / "open_questions.jsonl"
        questions_path.touch()

        docs, titles = build_conversation_documents(
            input_json, atoms_path, decisions_path, questions_path
        )

        assert "conv-1" in docs
        assert "Empty Conversation" in docs["conv-1"]
        # Should still have title even if no artifacts
        assert docs["conv-1"].startswith("Title: Empty Conversation")
