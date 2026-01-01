"""CLI smoke tests (offline, using fake adapters)."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from typer.testing import CliRunner

from ck_exporter.cli import app


@pytest.fixture
def sample_export_file(tmp_path: Path) -> Path:
    """Create a sample export JSON file."""
    export_data = [
        {
            "id": "test-conv-1",
            "conversation_id": "test-conv-1",
            "title": "Test Conversation",
            "mapping": {
                "msg-1": {
                    "id": "msg-1",
                    "parent": None,
                    "message": {
                        "id": "msg-1",
                        "author": {"role": "user"},
                        "create_time": 1704067200.0,
                        "content": {"parts": ["Hello, this is a test message."]},
                    },
                }
            },
            "current_node": "msg-1",
        }
    ]
    export_path = tmp_path / "export.json"
    with export_path.open("w") as f:
        json.dump(export_data, f)
    return export_path


def test_cli_linearize_command(sample_export_file: Path, tmp_path: Path):
    """Test that linearize command runs without errors."""
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "linearize",
            "--input",
            str(sample_export_file),
            "--out",
            str(tmp_path / "evidence"),
        ],
    )
    assert result.exit_code == 0
    # Check that output was created
    evidence_path = tmp_path / "evidence" / "test-conv-1" / "conversation.md"
    assert evidence_path.exists()


def test_cli_compile_command(tmp_path: Path):
    """Test that compile command runs without errors (with empty atoms)."""
    atoms_dir = tmp_path / "atoms"
    atoms_dir.mkdir()
    # Create empty conversation dir
    (atoms_dir / "test-conv-1").mkdir()

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "compile",
            "--atoms",
            str(atoms_dir),
            "--out",
            str(tmp_path / "docs"),
        ],
    )
    # Should succeed even with empty atoms
    assert result.exit_code == 0


def test_cli_consolidate_command(tmp_path: Path):
    """Test that consolidate command runs without errors (with empty dirs)."""
    atoms_dir = tmp_path / "atoms"
    docs_dir = tmp_path / "docs"
    out_dir = tmp_path / "output"
    atoms_dir.mkdir()
    docs_dir.mkdir()

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "consolidate",
            "--atoms",
            str(atoms_dir),
            "--docs",
            str(docs_dir),
            "--out",
            str(out_dir),
            "--no-include-docs",
        ],
    )
    assert result.exit_code == 0
    # Check that output was created
    manifest_path = out_dir / "project" / "manifest.md"
    assert manifest_path.exists()


def test_cli_log_mode_human(sample_export_file: Path, tmp_path: Path):
    """Test that --log-mode human produces non-JSON console output."""
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "--log-mode",
            "human",
            "linearize",
            "--input",
            str(sample_export_file),
            "--out",
            str(tmp_path / "evidence"),
        ],
    )
    assert result.exit_code == 0
    # In human mode, stderr should not contain JSON log lines
    # (Rich output is harder to test, but we can verify it's not JSON)
    stderr_lines = result.stderr.split("\n")
    json_lines = [line for line in stderr_lines if line.strip().startswith("{")]
    # Should have minimal or no JSON lines in human mode
    assert len(json_lines) == 0 or len(json_lines) < len(stderr_lines) / 2


def test_cli_log_mode_hybrid_creates_json_file(sample_export_file: Path, tmp_path: Path):
    """Test that --log-mode hybrid --log-file creates a JSON log file."""
    log_file = tmp_path / "test_logs.jsonl"
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "--log-mode",
            "hybrid",
            "--log-file",
            str(log_file),
            "linearize",
            "--input",
            str(sample_export_file),
            "--out",
            str(tmp_path / "evidence"),
        ],
    )
    assert result.exit_code == 0
    # Check that log file was created
    assert log_file.exists()
    # Check that log file contains JSON lines
    with log_file.open() as f:
        lines = [line.strip() for line in f if line.strip()]
        assert len(lines) > 0
        # Verify first line is valid JSON
        first_log = json.loads(lines[0])
        assert "ts" in first_log
        assert "level" in first_log
        assert "logger" in first_log
        assert "message" in first_log


def test_cli_log_mode_machine_creates_json_file(sample_export_file: Path, tmp_path: Path):
    """Test that --log-mode machine --log-file creates JSON logs only."""
    log_file = tmp_path / "test_logs.jsonl"
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "--log-mode",
            "machine",
            "--log-file",
            str(log_file),
            "linearize",
            "--input",
            str(sample_export_file),
            "--out",
            str(tmp_path / "evidence"),
        ],
    )
    assert result.exit_code == 0
    # Check that log file was created
    assert log_file.exists()
    # Check that log file contains JSON lines
    with log_file.open() as f:
        lines = [line.strip() for line in f if line.strip()]
        assert len(lines) > 0
        # Verify logs are valid JSON
        for line in lines:
            log_entry = json.loads(line)
            assert "ts" in log_entry
            assert "level" in log_entry


def test_cli_log_mode_auto_detects_tty(sample_export_file: Path, tmp_path: Path):
    """Test that --log-mode auto works (basic smoke test)."""
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "--log-mode",
            "auto",
            "linearize",
            "--input",
            str(sample_export_file),
            "--out",
            str(tmp_path / "evidence"),
        ],
    )
    assert result.exit_code == 0
    # Auto mode should work without errors
    evidence_path = tmp_path / "evidence" / "test-conv-1" / "conversation.md"
    assert evidence_path.exists()


def test_run_all_no_dashboard_flag(sample_export_file: Path, tmp_path: Path):
    """Test that --no-dashboard flag works and doesn't crash."""
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "--no-dashboard",
            "run-all",
            "--input",
            str(sample_export_file),
            "--evidence",
            str(tmp_path / "evidence"),
            "--atoms",
            str(tmp_path / "atoms"),
            "--docs",
            str(tmp_path / "docs"),
        ],
    )
    # Should complete successfully (even if non-TTY)
    assert result.exit_code == 0


def test_run_all_dashboard_flag_non_tty(sample_export_file: Path, tmp_path: Path):
    """Test that --dashboard doesn't crash in non-TTY (should auto-disable or fallback)."""
    runner = CliRunner()
    # CliRunner simulates non-TTY environment
    result = runner.invoke(
        app,
        [
            "--dashboard",
            "run-all",
            "--input",
            str(sample_export_file),
            "--evidence",
            str(tmp_path / "evidence"),
            "--atoms",
            str(tmp_path / "atoms"),
            "--docs",
            str(tmp_path / "docs"),
        ],
    )
    # Should handle gracefully (either disable dashboard or run without it)
    assert result.exit_code == 0


def test_run_all_split_by_subdir(tmp_path: Path):
    """Test that run-all splits outputs by typed subdirectories."""
    # Create a dataset directory with typed subfolders
    dataset_dir = tmp_path / "test_dataset"
    dataset_dir.mkdir()

    # Create documents subfolder with a minimal markdown file
    documents_dir = dataset_dir / "documents"
    documents_dir.mkdir()
    (documents_dir / "test_doc.md").write_text("# Test Document\n\nThis is a test document.")

    # Create meeting_artifacts subfolder with a minimal markdown file
    meetings_dir = dataset_dir / "meeting_artifacts"
    meetings_dir.mkdir()
    (meetings_dir / "test_meeting.md").write_text("# Test Meeting\n\n## Notes\n\nMeeting notes here.")

    # Create ai_conversations subfolder with a minimal JSON conversation
    ai_dir = dataset_dir / "ai_conversations"
    ai_dir.mkdir()
    ai_conv = {
        "id": "test-ai-conv",
        "conversation_id": "test-ai-conv",
        "title": "Test AI Conversation",
        "mapping": {
            "msg-1": {
                "id": "msg-1",
                "parent": None,
                "message": {
                    "id": "msg-1",
                    "author": {"role": "user"},
                    "create_time": 1704067200.0,
                    "content": {"parts": ["Hello, this is a test message."]},
                },
            }
        },
        "current_node": "msg-1",
    }
    (ai_dir / "test_ai.json").write_text(json.dumps(ai_conv))

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "--no-dashboard",
            "run-all",
            "--input",
            str(dataset_dir),
        ],
    )
    assert result.exit_code == 0

    # Verify that separate output trees were created for each type
    # Documents
    assert (tmp_path / "_evidence_test_dataset_documents").exists()
    assert (tmp_path / "_atoms_test_dataset_documents").exists()
    assert (tmp_path / "output" / "test_dataset" / "documents" / "docs").exists()

    # Meetings
    assert (tmp_path / "_evidence_test_dataset_meetings").exists()
    assert (tmp_path / "_atoms_test_dataset_meetings").exists()
    assert (tmp_path / "output" / "test_dataset" / "meetings" / "docs").exists()

    # AI
    assert (tmp_path / "_evidence_test_dataset_ai").exists()
    assert (tmp_path / "_atoms_test_dataset_ai").exists()
    assert (tmp_path / "output" / "test_dataset" / "ai" / "docs").exists()

    # Verify that at least one conversation folder exists in each evidence dir
    # (actual content depends on parsing, but structure should be there)
    doc_evidence_dirs = list((tmp_path / "_evidence_test_dataset_documents").iterdir())
    meeting_evidence_dirs = list((tmp_path / "_evidence_test_dataset_meetings").iterdir())
    ai_evidence_dirs = list((tmp_path / "_evidence_test_dataset_ai").iterdir())

    # At least one conversation should have been processed
    assert len(doc_evidence_dirs) > 0 or len(meeting_evidence_dirs) > 0 or len(ai_evidence_dirs) > 0


def test_run_all_split_by_subdir_with_explicit_outputs(tmp_path: Path):
    """Test that split-by-subdir creates typed subfolders under explicit output roots."""
    # Create a dataset directory with typed subfolders
    dataset_dir = tmp_path / "test_dataset"
    dataset_dir.mkdir()

    # Create documents subfolder with a minimal markdown file
    documents_dir = dataset_dir / "documents"
    documents_dir.mkdir()
    (documents_dir / "test_doc.md").write_text("# Test Document\n\nThis is a test document.")

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "--no-dashboard",
            "run-all",
            "--input",
            str(dataset_dir),
            "--evidence",
            str(tmp_path / "custom_evidence"),
            "--atoms",
            str(tmp_path / "custom_atoms"),
            "--docs",
            str(tmp_path / "custom_docs"),
        ],
    )
    assert result.exit_code == 0

    # Verify that typed subfolders were created under explicit roots
    assert (tmp_path / "custom_evidence" / "documents").exists()
    assert (tmp_path / "custom_atoms" / "documents").exists()
    assert (tmp_path / "custom_docs" / "documents").exists()
