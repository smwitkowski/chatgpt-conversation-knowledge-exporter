"""Compile documentation from knowledge atoms."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# Template directory (will be set relative to this file)
TEMPLATE_DIR = Path(__file__).parent / "templates"


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

    # Load atoms
    facts = load_atoms_jsonl(conv_atoms_dir / "facts.jsonl")
    decisions = load_atoms_jsonl(conv_atoms_dir / "decisions.jsonl")
    questions = load_atoms_jsonl(conv_atoms_dir / "open_questions.jsonl")

    if not facts and not decisions and not questions:
        console.print(f"[yellow]No atoms found for {conversation_id}[/yellow]")
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
        if adr_template:
            adr_content = adr_template.render(
                adr_number=idx,
                decision=decision,
                conversation_id=conversation_id,
            )
            adr_path = adr_output_dir / f"ADR-{idx:04d}-{decision.get('topic', 'decision').replace(' ', '-')}.md"
            adr_path.write_text(adr_content, encoding="utf-8")
        else:
            # Fallback: simple markdown
            adr_path = adr_output_dir / f"ADR-{idx:04d}-{decision.get('topic', 'decision').replace(' ', '-')}.md"
            adr_content = f"""# ADR {idx:04d}: {decision.get('statement', 'Decision')}

**Status**: {decision.get('status', 'active')}
**Topic**: {decision.get('topic', 'uncategorized')}

## Decision

{decision.get('statement', '')}

## Rationale

{decision.get('rationale', 'Not provided')}

## Alternatives Considered

{chr(10).join(f"- {alt}" for alt in decision.get('alternatives', [])) or 'None listed'}

## Consequences

{decision.get('consequences', 'Not specified')}

## Evidence

{chr(10).join(f"- Message ID: {e.get('message_id')} at {e.get('time_iso')}" for e in decision.get('evidence', []))}
"""
            adr_path.write_text(adr_content, encoding="utf-8")

    console.print(f"[green]  ✓ Compiled docs for {conversation_id}[/green]")


def compile_docs(atoms_dir: Path, output_dir: Path) -> None:
    """Compile documentation for all conversations."""
    if not atoms_dir.exists():
        raise ValueError(f"Atoms directory not found: {atoms_dir}")

    conversation_dirs = [d for d in atoms_dir.iterdir() if d.is_dir()]

    if not conversation_dirs:
        console.print("[yellow]No conversation directories found[/yellow]")
        return

    console.print(f"[bold]Compiling docs for {len(conversation_dirs)} conversations[/bold]")

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
                console.print(f"[red]Error compiling {conv_id}: {e}[/red]")

            progress.advance(task)

    console.print(f"[bold green]✓ Compilation complete[/bold green]")
