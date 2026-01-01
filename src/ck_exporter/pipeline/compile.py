"""Compile documentation from knowledge atoms."""

import json
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ck_exporter.logging import get_logger, should_show_progress, with_context
from ck_exporter.pipeline.legacy_adapter import load_universal_atoms

logger = get_logger(__name__)

# Template directory (relative to templates folder in src/ck_exporter)
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be safe for use in filenames.
    
    Removes or replaces characters that are invalid on common filesystems:
    - Windows: < > : " / \\ | ? *
    - Unix/Linux: / and null bytes
    - Control characters (0x00-0x1f)
    
    Also handles:
    - Leading/trailing whitespace and dots
    - Empty strings after sanitization
    - Overly long names (limits to 200 chars)
    
    Args:
        name: The string to sanitize
        
    Returns:
        A filesystem-safe string
    """
    if not name or not isinstance(name, str):
        return "unnamed"
    
    # Replace invalid characters with hyphens
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '-', name)
    
    # Replace multiple consecutive spaces/hyphens with single hyphen
    sanitized = re.sub(r'[\s\-]+', '-', sanitized)
    
    # Remove leading/trailing dots, spaces, and hyphens
    sanitized = sanitized.strip('. -')
    
    # Limit length to prevent filesystem issues
    sanitized = sanitized[:200]
    
    # If empty after sanitization, use default
    return sanitized if sanitized else "unnamed"


def load_atoms_jsonl(file_path: Path) -> List[Dict[str, Any]]:
    """Load atoms from a JSONL file."""
    if not file_path.exists():
        return []

    atoms = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    atoms.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    return atoms


def group_atoms_by_topic(atoms: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group atoms by topic."""
    grouped = {}
    for atom in atoms:
        topic = atom.get("topic", "uncategorized")
        if topic not in grouped:
            grouped[topic] = []
        grouped[topic].append(atom)
    return grouped


def compile_conversation_docs(
    conversation_id: str,
    atoms_dir: Path,
    output_dir: Path,
    title: Optional[str] = None,
) -> None:
    """Compile docs for a single conversation."""
    conv_atoms_dir = atoms_dir / conversation_id

    # Load universal atoms (falls back to legacy if needed)
    all_atoms = load_universal_atoms(conv_atoms_dir)

    # Filter by kind for backward compatibility
    facts = [a for a in all_atoms if a.get("kind") in ["fact", "definition", "requirement", "metric", "assumption", "constraint", "idea"]]
    decisions = [a for a in all_atoms if a.get("kind") == "decision"]
    questions = [a for a in all_atoms if a.get("kind") == "open_question"]
    action_items = [a for a in all_atoms if a.get("kind") == "action_item"]
    meeting_topics = [a for a in all_atoms if a.get("kind") == "meeting_topic"]
    risks = [a for a in all_atoms if a.get("kind") == "risk"]
    blockers = [a for a in all_atoms if a.get("kind") == "blocker"]
    dependencies = [a for a in all_atoms if a.get("kind") == "dependency"]

    conv_logger = with_context(logger, conversation_id=conversation_id)

    if not all_atoms:
        conv_logger.warning(
            "No atoms found",
            extra={"event": "compile.conversation.skipped", "reason": "no_atoms"},
        )
        return

    # Setup Jinja2 environment
    if TEMPLATE_DIR.exists():
        env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            autoescape=select_autoescape(["html", "xml"]),
        )
    else:
        # Fallback: create basic templates inline
        env = Environment(loader=FileSystemLoader("."))

    # Create output directory
    conv_output_dir = output_dir / conversation_id
    conv_output_dir.mkdir(parents=True, exist_ok=True)

    # Compile overview
    overview_template = env.get_template("overview.md.j2") if TEMPLATE_DIR.exists() else None
    if overview_template:
        overview_content = overview_template.render(
            conversation_id=conversation_id,
            title=title or f"Conversation {conversation_id}",
            facts=facts,
            decisions=decisions,
            questions=questions,
            action_items=action_items,
        )
        (conv_output_dir / "overview.md").write_text(overview_content, encoding="utf-8")

    # Compile architecture doc
    arch_facts = [f for f in facts if f.get("topic", "").lower() in ["architecture", "pipeline", "storage", "integrations"]]
    if arch_facts:
        arch_template = env.get_template("architecture.md.j2") if TEMPLATE_DIR.exists() else None
        if arch_template:
            arch_content = arch_template.render(
                conversation_id=conversation_id,
                facts=arch_facts,
                decisions=[d for d in decisions if d.get("topic", "").lower() in ["architecture", "pipeline", "storage", "integrations"]],
            )
            (conv_output_dir / "architecture.md").write_text(arch_content, encoding="utf-8")

    # Compile ADRs
    adr_output_dir = output_dir / "decisions" / conversation_id
    adr_output_dir.mkdir(parents=True, exist_ok=True)

    adr_template = env.get_template("adr.md.j2") if TEMPLATE_DIR.exists() else None
    for idx, decision in enumerate(decisions, start=1):
        # Sanitize topic for use in filename
        topic_safe = sanitize_filename(decision.get('topic', 'decision'))
        
        if adr_template:
            adr_content = adr_template.render(
                adr_number=idx,
                decision=decision,
                conversation_id=conversation_id,
            )
            adr_path = adr_output_dir / f"ADR-{idx:04d}-{topic_safe}.md"
            adr_path.write_text(adr_content, encoding="utf-8")
        else:
            # Fallback: simple markdown
            adr_path = adr_output_dir / f"ADR-{idx:04d}-{topic_safe}.md"
            # Extract decision fields from universal atom meta
            meta = decision.get('meta', {})
            decision_meta = meta.get('decision', {})
            rationale = decision_meta.get('rationale', 'Not provided')
            alternatives = decision_meta.get('alternatives', [])
            consequences = decision_meta.get('consequences', 'Not specified')
            
            adr_content = f"""# ADR {idx:04d}: {decision.get('statement', 'Decision')}

**Status**: {decision.get('status', 'active')}
**Topic**: {decision.get('topic', 'uncategorized')}

## Decision

{decision.get('statement', '')}

## Rationale

{rationale}

## Alternatives Considered

{chr(10).join(f"- {alt}" for alt in alternatives) or 'None listed'}

## Consequences

{consequences}

## Evidence

{chr(10).join(f"- Message ID: {e.get('message_id')} at {e.get('time_iso')}" for e in decision.get('evidence', []))}
"""
            adr_path.write_text(adr_content, encoding="utf-8")

    # Compile action items doc (if any)
    if action_items:
        action_items_content = "# Action Items\n\n"
        for idx, ai in enumerate(action_items, start=1):
            statement = ai.get("statement", "")
            status = ai.get("status", "active")
            meta = ai.get("meta", {})
            task_meta = meta.get("task", {}) or meta.get("meeting", {}).get("task", {})
            owner = task_meta.get("owner")
            due = task_meta.get("due")
            
            evidence_list = ai.get("evidence", [])
            evidence_text = ""
            if evidence_list:
                ev = evidence_list[0]
                msg_id = ev.get("message_id", "")
                if msg_id:
                    evidence_text = f" (from {msg_id})"
            
            owner_text = f" - Owner: {owner}" if owner else ""
            due_text = f" - Due: {due}" if due else ""
            status_text = f" [{status}]" if status != "active" else ""
            
            action_items_content += f"{idx}. {statement}{status_text}{owner_text}{due_text}{evidence_text}\n\n"
        (conv_output_dir / "action_items.md").write_text(action_items_content, encoding="utf-8")

    # Compile meeting topics doc (if any)
    if meeting_topics:
        topics_content = "# Meeting Topics\n\n"
        for idx, topic in enumerate(meeting_topics, start=1):
            statement = topic.get("statement", "")
            meta = topic.get("meta", {})
            summary = meta.get("meeting", {}).get("topic", {}).get("summary")
            if summary:
                topics_content += f"{idx}. **{statement}**\n   {summary}\n\n"
            else:
                topics_content += f"{idx}. {statement}\n\n"
        (conv_output_dir / "meeting_topics.md").write_text(topics_content, encoding="utf-8")

    # Compile risks/blockers/dependencies doc (if any)
    issues = risks + blockers + dependencies
    if issues:
        issues_content = "# Risks, Blockers, and Dependencies\n\n"
        if risks:
            issues_content += "## Risks\n\n"
            for idx, risk in enumerate(risks, start=1):
                statement = risk.get("statement", "")
                status = risk.get("status", "open")
                meta = risk.get("meta", {})
                owner = meta.get("issue", {}).get("owner")
                status_text = f" [{status}]" if status != "open" else ""
                owner_text = f" - Owner: {owner}" if owner else ""
                issues_content += f"{idx}. {statement}{status_text}{owner_text}\n\n"
        if blockers:
            issues_content += "## Blockers\n\n"
            for idx, blocker in enumerate(blockers, start=1):
                statement = blocker.get("statement", "")
                status = blocker.get("status", "open")
                meta = blocker.get("meta", {})
                owner = meta.get("issue", {}).get("owner")
                blocked_by = meta.get("issue", {}).get("blocked_by")
                status_text = f" [{status}]" if status != "open" else ""
                owner_text = f" - Owner: {owner}" if owner else ""
                blocked_by_text = f" - Blocked by: {blocked_by}" if blocked_by else ""
                issues_content += f"{idx}. {statement}{status_text}{owner_text}{blocked_by_text}\n\n"
        if dependencies:
            issues_content += "## Dependencies\n\n"
            for idx, dep in enumerate(dependencies, start=1):
                statement = dep.get("statement", "")
                status = dep.get("status", "open")
                meta = dep.get("meta", {})
                owner = meta.get("issue", {}).get("owner")
                depends_on = meta.get("issue", {}).get("depends_on")
                status_text = f" [{status}]" if status != "open" else ""
                owner_text = f" - Owner: {owner}" if owner else ""
                depends_on_text = f" - Depends on: {depends_on}" if depends_on else ""
                issues_content += f"{idx}. {statement}{status_text}{owner_text}{depends_on_text}\n\n"
        (conv_output_dir / "risks.md").write_text(issues_content, encoding="utf-8")

    conv_logger.info(
        "Compiled docs",
        extra={
            "event": "compile.conversation.complete",
            "num_facts": len(facts),
            "num_decisions": len(decisions),
            "num_questions": len(questions),
            "num_action_items": len(action_items),
            "num_meeting_topics": len(meeting_topics),
            "num_risks": len(risks),
            "num_blockers": len(blockers),
            "num_dependencies": len(dependencies),
        },
    )


def compile_docs(
    atoms_dir: Path,
    output_dir: Path,
    progress_cb: Optional[Callable[[int, int, Optional[dict]], None]] = None,
) -> None:
    """
    Compile documentation for all conversations.

    Args:
        atoms_dir: Directory containing conversation atom directories
        output_dir: Output directory for compiled docs
        progress_cb: Optional callback(completed, total, context) for progress updates
    """
    if not atoms_dir.exists():
        raise ValueError(f"Atoms directory not found: {atoms_dir}")

    conversation_dirs = [d for d in atoms_dir.iterdir() if d.is_dir()]

    if not conversation_dirs:
        logger.warning(
            "No conversation directories found",
            extra={"event": "compile.export.empty"},
        )
        return

    logger.info(
        "Compiling docs",
        extra={
            "event": "compile.export.start",
            "num_conversations": len(conversation_dirs),
        },
    )

    # Notify progress callback of total
    if progress_cb:
        progress_cb(0, len(conversation_dirs), {})

    if should_show_progress() and not progress_cb:
        console = Console(stderr=True)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Compiling docs...", total=len(conversation_dirs))

            for conv_dir in conversation_dirs:
                conv_id = conv_dir.name
                try:
                    compile_conversation_docs(conv_id, atoms_dir, output_dir)
                except Exception as e:
                    logger.exception(
                        "Error compiling conversation",
                        extra={
                            "event": "compile.conversation.error",
                            "conversation_id": conv_id,
                        },
                    )

                progress.advance(task)
    else:
        # Non-interactive mode or dashboard mode: process without progress bar
        completed = 0
        for conv_dir in conversation_dirs:
            conv_id = conv_dir.name
            try:
                compile_conversation_docs(conv_id, atoms_dir, output_dir)
            except Exception as e:
                logger.exception(
                    "Error compiling conversation",
                    extra={
                        "event": "compile.conversation.error",
                        "conversation_id": conv_id,
                    },
                )
            completed += 1
            if progress_cb:
                progress_cb(completed, len(conversation_dirs), {"conversation_id": conv_id})

    logger.info(
        "Compilation complete",
        extra={"event": "compile.export.complete"},
    )
