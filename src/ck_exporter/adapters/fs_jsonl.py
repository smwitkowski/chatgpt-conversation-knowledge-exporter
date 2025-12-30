"""File system JSONL read/write utilities."""

import json
from pathlib import Path
from typing import Any, Iterable


def read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    """
    Read JSONL file and yield each JSON object.

    Args:
        path: Path to JSONL file

    Yields:
        Dict objects parsed from each line
    """
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                yield obj


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    """
    Write list of dicts to JSONL file (atomic write via temp file).

    Args:
        path: Output path
        rows: List of dict objects to write
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write to temp file first, then rename (atomic write)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    temp_path.replace(path)


def load_atoms_jsonl(file_path: Path) -> list[dict[str, Any]]:
    """
    Load atoms from a JSONL file.

    Args:
        file_path: Path to JSONL file

    Returns:
        List of atom dicts
    """
    if not file_path.exists():
        return []

    atoms = []
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    atoms.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    return atoms
