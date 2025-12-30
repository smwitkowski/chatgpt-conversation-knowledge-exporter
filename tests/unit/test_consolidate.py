"""Unit tests for consolidation logic."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from ck_exporter.pipeline.consolidate import (
    ConsolidateStats,
    _merge_evidence,
    _normalize_evidence_key,
    consolidate_project,
)


def test_normalize_evidence_key():
    """Test evidence key normalization."""
    ev = {
        "conversation_id": "conv-1",
        "message_id": "msg-1",
        "time_iso": "2025-01-01T00:00:00",
    }
    key = _normalize_evidence_key(ev)
    assert key == ("conv-1", "msg-1", "2025-01-01T00:00:00")


def test_normalize_evidence_key_missing_fields():
    """Test evidence key with missing fields."""
    ev = {"message_id": "msg-1"}
    key = _normalize_evidence_key(ev)
    assert key == ("", "msg-1", "")


def test_normalize_evidence_key_invalid_type():
    """Test evidence key with invalid type."""
    key = _normalize_evidence_key("not a dict")
    assert key is None


def test_merge_evidence_deduplicates():
    """Test that evidence merge deduplicates."""
    existing = [
        {"conversation_id": "conv-1", "message_id": "msg-1", "time_iso": "2025-01-01T00:00:00"}
    ]
    incoming = [
        {"conversation_id": "conv-1", "message_id": "msg-1", "time_iso": "2025-01-01T00:00:00"}
    ]
    merged = _merge_evidence(existing, incoming, "conv-1")
    assert len(merged) == 1


def test_merge_evidence_adds_conversation_id():
    """Test that merge adds conversation_id to evidence."""
    existing = []
    incoming = [{"message_id": "msg-1", "time_iso": "2025-01-01T00:00:00"}]
    merged = _merge_evidence(existing, incoming, "conv-1")
    assert len(merged) == 1
    assert merged[0]["conversation_id"] == "conv-1"


def test_consolidate_project_empty_dirs(tmp_path: Path):
    """Test consolidation with empty directories."""
    atoms_dir = tmp_path / "atoms"
    docs_dir = tmp_path / "docs"
    out_dir = tmp_path / "output"
    atoms_dir.mkdir()
    docs_dir.mkdir()

    stats = consolidate_project(atoms_dir, docs_dir, out_dir, include_docs=False)
    assert stats.atoms_in == 0
    assert stats.atoms_out == 0
    assert stats.decisions_in == 0
    assert stats.decisions_out == 0
