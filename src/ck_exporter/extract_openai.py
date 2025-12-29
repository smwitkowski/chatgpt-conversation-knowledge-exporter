"""OpenAI-backed knowledge atom extraction."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from tenacity import retry, stop_after_attempt, wait_exponential

from ck_exporter.atoms_schema import Atom, DecisionAtom, OpenQuestion
from ck_exporter.chunking import chunk_messages
from ck_exporter.export_schema import get_conversation_id, get_title
from ck_exporter.linearize import linearize_conversation

load_dotenv()

console = Console()

# Extraction prompt template
EXTRACTION_PROMPT = """You are extracting structured knowledge from a conversation about a project.

Analyze the following conversation chunk and extract:
1. **Facts**: Concrete statements about the project (what it is, how it works, etc.)
2. **Decisions**: Explicit or implicit decisions made (with alternatives and rationale if available)
3. **Open Questions**: Unresolved questions or uncertainties mentioned

For each item, provide:
- type: one of decision|requirement|definition|metric|risk|assumption|constraint|idea|fact
- topic: category (e.g., "pricing", "architecture", "ICP", "content", "evals", "marketing")
- statement: the actual knowledge statement
- status: active|deprecated|uncertain
- evidence: array with message_id and time_iso pointing to source messages

For decisions, also include:
- alternatives: what other options were considered
- rationale: why this decision was made
- consequences: expected outcomes

Return valid JSON matching this schema:
{{
  "facts": [
    {{
      "type": "fact|definition|requirement|metric|constraint",
      "topic": "...",
      "statement": "...",
      "status": "active",
      "evidence": [{{"message_id": "...", "time_iso": "..."}}]
    }}
  ],
  "decisions": [
    {{
      "type": "decision",
      "topic": "...",
      "statement": "...",
      "status": "active",
      "alternatives": ["..."],
      "rationale": "...",
      "consequences": "...",
      "evidence": [{{"message_id": "...", "time_iso": "..."}}]
    }}
  ],
  "open_questions": [
    {{
      "question": "...",
      "topic": "...",
      "context": "...",
      "evidence": [{{"message_id": "...", "time_iso": "..."}}]
    }}
  ]
}}

Conversation chunk:
{chunk_text}
"""


def format_chunk_for_extraction(messages: List[Dict[str, Any]]) -> str:
    """Format a message chunk as text for extraction."""
    lines = []
    for msg in messages:
        role = msg.get("role", "unknown")
        text = msg.get("text", "")
        time_iso = msg.get("time_iso", "")
        msg_id = msg.get("id", "")

        lines.append(f"[{role.upper()}] {time_iso} (ID: {msg_id})")
        lines.append(text)
        lines.append("")

    return "\n".join(lines)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def extract_atoms_from_chunk(
    chunk_text: str,
    client: OpenAI,
    model: str = "gpt-5.2",
) -> Dict[str, Any]:
    """Call OpenAI to extract atoms from a conversation chunk."""
    prompt = EXTRACTION_PROMPT.format(chunk_text=chunk_text)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a knowledge extraction assistant. Return only valid JSON."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    content = response.choices[0].message.content
    if not content:
        return {"facts": [], "decisions": [], "open_questions": []}

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        console.print(f"[red]JSON decode error: {e}[/red]")
        console.print(f"[dim]Response: {content[:200]}...[/dim]")
        return {"facts": [], "decisions": [], "open_questions": []}


def write_atoms_jsonl(atoms: List[Dict[str, Any]], output_path: Path) -> None:
    """Append atoms to a JSONL file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "a", encoding="utf-8") as f:
        for atom in atoms:
            f.write(json.dumps(atom, ensure_ascii=False) + "\n")


def extract_conversation(
    conversation: Dict[str, Any],
    evidence_dir: Path,
    atoms_dir: Path,
    client: OpenAI,
    model: str = "gpt-5.2",
    max_chunk_tokens: int = 8000,
) -> None:
    """Extract atoms from a single conversation."""
    conv_id = get_conversation_id(conversation)
    if not conv_id:
        console.print("[yellow]Skipping conversation without ID[/yellow]")
        return

    # Load linearized messages from evidence
    evidence_path = evidence_dir / conv_id / "conversation.md"
    if not evidence_path.exists():
        console.print(f"[yellow]No evidence found for {conv_id}, linearizing...[/yellow]")
        messages = linearize_conversation(conversation)
    else:
        # Re-linearize to get message structure
        messages = linearize_conversation(conversation)

    if not messages:
        console.print(f"[yellow]No messages found for {conv_id}[/yellow]")
        return

    # Chunk messages
    chunks = chunk_messages(messages, max_tokens=max_chunk_tokens, model=model)

    console.print(f"[cyan]  Processing {conv_id}: {len(chunks)} chunks, {len(messages)} messages[/cyan]")

    all_facts = []
    all_decisions = []
    all_questions = []

    for i, chunk in enumerate(chunks, 1):
        console.print(f"[dim]    Chunk {i}/{len(chunks)}...[/dim]", end="")
        chunk_text = format_chunk_for_extraction(chunk)
        result = extract_atoms_from_chunk(chunk_text, client, model)

        # Collect atoms
        chunk_facts = result.get("facts", [])
        chunk_decisions = result.get("decisions", [])
        chunk_questions = result.get("open_questions", [])

        for fact in chunk_facts:
            all_facts.append(fact)
        for decision in chunk_decisions:
            all_decisions.append(decision)
        for question in chunk_questions:
            all_questions.append(question)

        console.print(f" [green]✓[/green] ({len(chunk_facts)} facts, {len(chunk_decisions)} decisions, {len(chunk_questions)} questions)")

    # Write JSONL files
    facts_path = atoms_dir / conv_id / "facts.jsonl"
    decisions_path = atoms_dir / conv_id / "decisions.jsonl"
    questions_path = atoms_dir / conv_id / "open_questions.jsonl"

    if all_facts:
        write_atoms_jsonl(all_facts, facts_path)
    if all_decisions:
        write_atoms_jsonl(all_decisions, decisions_path)
    if all_questions:
        write_atoms_jsonl(all_questions, questions_path)

    console.print(f"[green]  ✓ Extracted {len(all_facts)} facts, {len(all_decisions)} decisions, {len(all_questions)} questions[/green]")


def extract_export(
    input_path: Path,
    evidence_dir: Path,
    atoms_dir: Path,
    model: Optional[str] = None,
    conversation_id: Optional[str] = None,
) -> None:
    """Process export and extract atoms for all conversations (or a single one if conversation_id is provided)."""
    import os

    import json

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment")

    model = model or os.getenv("OPENAI_MODEL", "gpt-5.2")
    client = OpenAI(api_key=api_key)

    console.print(f"[bold]Loading export from[/bold] {input_path}")
    console.print(f"[bold]Using model:[/bold] {model}")

    with open(input_path, "r", encoding="utf-8") as f:
        conversations = json.load(f)

    if not isinstance(conversations, list):
        raise ValueError("Expected top-level list of conversations")

    # Filter to single conversation if requested
    if conversation_id:
        conversations = [
            conv
            for conv in conversations
            if get_conversation_id(conv) == conversation_id
        ]
        if not conversations:
            console.print(f"[red]Conversation {conversation_id} not found in export[/red]")
            raise typer.Exit(1)
        console.print(f"[yellow]Filtering to conversation: {conversation_id}[/yellow]")

    console.print(f"[green]Processing {len(conversations)} conversation(s)[/green]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Extracting atoms from {len(conversations)} conversation(s)...", total=len(conversations))

        for idx, conv in enumerate(conversations, 1):
            conv_id = get_conversation_id(conv) or "unknown"
            try:
                console.print(f"\n[bold][{idx}/{len(conversations)}][/bold] {conv_id}")
                extract_conversation(conv, evidence_dir, atoms_dir, client, model)
            except Exception as e:
                console.print(f"[red]Error processing {conv_id}: {e}[/red]")
                import traceback
                console.print(f"[dim]{traceback.format_exc()}[/dim]")

            progress.advance(task)

    console.print(f"\n[bold green]✓ Extraction complete[/bold green]")
