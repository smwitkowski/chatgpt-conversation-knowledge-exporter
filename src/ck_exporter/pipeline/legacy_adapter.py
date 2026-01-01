"""Legacy adapter for loading universal atoms (reads from atoms.jsonl)."""

import json
from pathlib import Path
from typing import Any, Dict, List


def load_universal_atoms(conv_atoms_dir: Path) -> List[Dict[str, Any]]:
    """
    Load universal atoms from a conversation directory.

    Reads from `atoms.jsonl` (universal format).
    Does not fall back to legacy split files (per plan: no legacy compatibility).

    Args:
        conv_atoms_dir: Directory containing atoms.jsonl

    Returns:
        List of universal atom dicts
    """
    atoms_path = conv_atoms_dir / "atoms.jsonl"
    if not atoms_path.exists():
        return []

    atoms = []
    with open(atoms_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                atom = json.loads(line)
                if isinstance(atom, dict):
                    atoms.append(atom)
            except json.JSONDecodeError:
                continue

    return atoms

