"""Consolidate per-conversation outputs into project-wide knowledge packet."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ck_exporter.logging import get_logger
from ck_exporter.pipeline.legacy_adapter import load_universal_atoms

logger = get_logger(__name__)

# Universal atoms file (single file per conversation)
ATOMS_FILE = "atoms.jsonl"


@dataclass
class ConsolidateStats:
    """Statistics from consolidation process."""

    atoms_in: int = 0
    atoms_out: int = 0
    atoms_by_kind: Dict[str, int] = None  # type: ignore

    def __post_init__(self):
        if self.atoms_by_kind is None:
            self.atoms_by_kind = {}


def _iter_conversation_dirs(atoms_dir: Path) -> List[Path]:
    """Get all conversation directories from atoms directory."""
    if not atoms_dir.exists():
        return []
    return sorted([p for p in atoms_dir.iterdir() if p.is_dir()], key=lambda p: p.name)


def _read_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    """Read JSONL file and yield each JSON object."""
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


def _normalize_evidence_key(ev: Any) -> Optional[Tuple[str, str, str]]:
    """Normalize evidence dict to a stable key for deduplication."""
    if not isinstance(ev, dict):
        return None
    return (
        str(ev.get("conversation_id") or ""),
        str(ev.get("message_id") or ""),
        str(ev.get("time_iso") or ""),
    )


def _merge_evidence(
    existing: List[Dict[str, Any]],
    incoming: List[Dict[str, Any]],
    conversation_id: str,
) -> List[Dict[str, Any]]:
    """Merge evidence arrays, deduplicating by (conversation_id, message_id, time_iso)."""
    merged: List[Dict[str, Any]] = []
    seen = set()

    def add_evidence(ev: Any, fallback_conv_id: str) -> None:
        """Add evidence if not already seen."""
        if not isinstance(ev, dict):
            return
        # Ensure conversation_id is present
        if "conversation_id" not in ev or not ev.get("conversation_id"):
            ev = {**ev, "conversation_id": fallback_conv_id}
        key = _normalize_evidence_key(ev)
        if key is None or key in seen:
            return
        seen.add(key)
        merged.append(ev)

    # Add existing evidence
    for ev in existing:
        add_evidence(ev, conversation_id)

    # Add incoming evidence
    for ev in incoming:
        add_evidence(ev, conversation_id)

    return merged


def _write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    """Write list of dicts to JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _concat_markdown_files(md_files: List[Path], out_path: Path) -> None:
    """Concatenate multiple markdown files into one."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    parts: List[str] = []
    for p in sorted(md_files):
        try:
            content = p.read_text(encoding="utf-8")
        except Exception:
            continue
        parts.append(f"\n\n---\n\n<!-- SOURCE_FILE: {p.as_posix()} -->\n\n{content}\n")
    out_path.write_text("".join(parts).lstrip(), encoding="utf-8")


def consolidate_project(
    atoms_dir: Path,
    docs_dir: Path,
    out_dir: Path,
    include_docs: bool = True,
) -> ConsolidateStats:
    """
    Consolidate per-conversation outputs into project-wide knowledge packet.

    Args:
        atoms_dir: Directory containing per-conversation atom JSONL files
        docs_dir: Directory containing per-conversation markdown docs
        out_dir: Output directory for consolidated files
        include_docs: Whether to concatenate markdown docs

    Returns:
        Statistics about the consolidation process
    """
    stats = ConsolidateStats()

    # Deduplication map: (kind, normalized_statement, topic?) -> consolidated atom
    atoms_by_key: Dict[Tuple[str, str, Optional[str]], Dict[str, Any]] = {}

    conversation_dirs = _iter_conversation_dirs(atoms_dir)
    logger.info(
        "Processing conversations",
        extra={
            "event": "consolidate.start",
            "num_conversations": len(conversation_dirs),
        },
    )

    for conv_dir in conversation_dirs:
        conv_id = conv_dir.name

        # Load universal atoms from atoms.jsonl
        atoms_path = conv_dir / ATOMS_FILE
        if not atoms_path.exists():
            logger.debug(
                "No atoms.jsonl found, skipping",
                extra={"event": "consolidate.conversation.skipped", "conversation_id": conv_id},
            )
            continue

        for atom in _read_jsonl(atoms_path):
            stats.atoms_in += 1
            kind = atom.get("kind", "fact")
            statement = str(atom.get("statement") or "").strip()
            topic = atom.get("topic")  # Optional

            # Track by kind
            stats.atoms_by_kind[kind] = stats.atoms_by_kind.get(kind, 0) + 1

            # Dedupe key: (kind, normalized_statement, topic)
            # Normalize statement: lowercase, strip whitespace
            normalized_statement = statement.lower().strip()
            key = (kind, normalized_statement, topic)

            if key in atoms_by_key:
                # Merge evidence
                existing_ev = atoms_by_key[key].get("evidence", [])
                incoming_ev = atom.get("evidence", [])
                atoms_by_key[key]["evidence"] = _merge_evidence(
                    existing_ev, incoming_ev, conv_id
                )
            else:
                # New atom, add source conversation ID
                atom = dict(atom)
                atom["source_conversation_id"] = conv_id
                # Ensure evidence has conversation_id
                ev_list = atom.get("evidence", [])
                for ev in ev_list:
                    if isinstance(ev, dict) and not ev.get("conversation_id"):
                        ev["conversation_id"] = conv_id
                atoms_by_key[key] = atom

    # Convert to list
    atoms_out = list(atoms_by_key.values())
    stats.atoms_out = len(atoms_out)

    # Write consolidated universal atoms file
    project_dir = out_dir / "project"
    logger.info(
        "Writing consolidated files",
        extra={
            "event": "consolidate.write",
            "project_dir": str(project_dir),
            "atoms_out": stats.atoms_out,
            "atoms_by_kind": stats.atoms_by_kind,
        },
    )

    _write_jsonl(project_dir / "atoms.jsonl", atoms_out)

    # Write manifest
    kind_summary = ", ".join([f"{kind}: {count}" for kind, count in sorted(stats.atoms_by_kind.items())])
    manifest_lines = [
        "# Project Knowledge Manifest",
        "",
        "## Statistics",
        "",
        f"- **Atoms**: {stats.atoms_in} input → {stats.atoms_out} output (deduped)",
        f"- **By Kind**: {kind_summary}",
        "",
        "## Files",
        "",
        "- `atoms.jsonl` - Consolidated universal atoms (schema v2)",
    ]

    if include_docs:
        manifest_lines.extend([
            "- `docs_concat.md` - Concatenated non-ADR documentation",
            "- `adrs_concat.md` - Concatenated ADR files",
        ])

    manifest_lines.append("")

    (project_dir / "manifest.md").write_text("\n".join(manifest_lines), encoding="utf-8")

    # Optionally concatenate markdown docs
    if include_docs and docs_dir.exists():
        # Find all non-ADR markdown files
        md_files = sorted([
            p
            for p in docs_dir.rglob("*.md")
            if "decisions" not in p.as_posix().replace("\\", "/")
        ])

        # Find all ADR files
        adr_files = sorted([
            p
            for p in (docs_dir / "decisions").rglob("*.md")
        ]) if (docs_dir / "decisions").exists() else []

        if md_files:
            logger.debug(
                "Concatenating markdown docs",
                extra={
                    "event": "consolidate.concat.docs",
                    "num_files": len(md_files),
                },
            )
            _concat_markdown_files(md_files, project_dir / "docs_concat.md")

        if adr_files:
            logger.debug(
                "Concatenating ADR files",
                extra={
                    "event": "consolidate.concat.adrs",
                    "num_files": len(adr_files),
                },
            )
            _concat_markdown_files(adr_files, project_dir / "adrs_concat.md")

    return stats
