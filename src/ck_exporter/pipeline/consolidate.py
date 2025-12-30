"""Consolidate per-conversation outputs into project-wide knowledge packet."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ck_exporter.logging import get_logger

logger = get_logger(__name__)

# File names to process
ATOM_FILES = ("facts.jsonl",)
DECISION_FILES = ("decisions.jsonl",)
QUESTION_FILES = ("open_questions.jsonl",)


@dataclass
class ConsolidateStats:
    """Statistics from consolidation process."""

    atoms_in: int = 0
    atoms_out: int = 0
    decisions_in: int = 0
    decisions_out: int = 0
    questions_in: int = 0
    questions_out: int = 0


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

    # Deduplication maps: key -> consolidated object
    atoms_by_key: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    decisions_by_key: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    questions_by_key: Dict[Tuple[str, str], Dict[str, Any]] = {}

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

        # Process atoms (facts.jsonl)
        for fn in ATOM_FILES:
            for atom in _read_jsonl(conv_dir / fn):
                stats.atoms_in += 1
                # Dedupe key: (type, topic, statement)
                key = (
                    str(atom.get("type") or ""),
                    str(atom.get("topic") or ""),
                    str(atom.get("statement") or ""),
                )
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

        # Process decisions (decisions.jsonl)
        for fn in DECISION_FILES:
            for d in _read_jsonl(conv_dir / fn):
                stats.decisions_in += 1
                # Dedupe key: (type, topic, statement)
                key = (
                    str(d.get("type") or "decision"),
                    str(d.get("topic") or ""),
                    str(d.get("statement") or ""),
                )
                if key in decisions_by_key:
                    # Merge evidence
                    existing_ev = decisions_by_key[key].get("evidence", [])
                    incoming_ev = d.get("evidence", [])
                    decisions_by_key[key]["evidence"] = _merge_evidence(
                        existing_ev, incoming_ev, conv_id
                    )
                else:
                    # New decision, add source conversation ID
                    d = dict(d)
                    d["source_conversation_id"] = conv_id
                    # Ensure evidence has conversation_id
                    ev_list = d.get("evidence", [])
                    for ev in ev_list:
                        if isinstance(ev, dict) and not ev.get("conversation_id"):
                            ev["conversation_id"] = conv_id
                    decisions_by_key[key] = d

        # Process open questions (open_questions.jsonl)
        for fn in QUESTION_FILES:
            for q in _read_jsonl(conv_dir / fn):
                stats.questions_in += 1
                # Dedupe key: (topic, question)
                key = (
                    str(q.get("topic") or ""),
                    str(q.get("question") or ""),
                )
                if key in questions_by_key:
                    # Merge evidence
                    existing_ev = questions_by_key[key].get("evidence", [])
                    incoming_ev = q.get("evidence", [])
                    questions_by_key[key]["evidence"] = _merge_evidence(
                        existing_ev, incoming_ev, conv_id
                    )
                else:
                    # New question, add source conversation ID
                    q = dict(q)
                    q["source_conversation_id"] = conv_id
                    # Ensure evidence has conversation_id
                    ev_list = q.get("evidence", [])
                    for ev in ev_list:
                        if isinstance(ev, dict) and not ev.get("conversation_id"):
                            ev["conversation_id"] = conv_id
                    questions_by_key[key] = q

    # Convert to lists
    atoms_out = list(atoms_by_key.values())
    decisions_out = list(decisions_by_key.values())
    questions_out = list(questions_by_key.values())

    stats.atoms_out = len(atoms_out)
    stats.decisions_out = len(decisions_out)
    stats.questions_out = len(questions_out)

    # Write consolidated JSONL files
    project_dir = out_dir / "project"
    logger.info(
        "Writing consolidated files",
        extra={
            "event": "consolidate.write",
            "project_dir": str(project_dir),
            "atoms_out": stats.atoms_out,
            "decisions_out": stats.decisions_out,
            "questions_out": stats.questions_out,
        },
    )

    _write_jsonl(project_dir / "atoms.jsonl", atoms_out)
    _write_jsonl(project_dir / "decisions.jsonl", decisions_out)
    _write_jsonl(project_dir / "open_questions.jsonl", questions_out)

    # Write manifest
    manifest_lines = [
        "# Project Knowledge Manifest",
        "",
        "## Statistics",
        "",
        f"- **Atoms**: {stats.atoms_in} input → {stats.atoms_out} output (deduped)",
        f"- **Decisions**: {stats.decisions_in} input → {stats.decisions_out} output (deduped)",
        f"- **Open Questions**: {stats.questions_in} input → {stats.questions_out} output (deduped)",
        "",
        "## Files",
        "",
        "- `atoms.jsonl` - Consolidated knowledge atoms",
        "- `decisions.jsonl` - Consolidated decisions/ADRs",
        "- `open_questions.jsonl` - Consolidated open questions",
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
