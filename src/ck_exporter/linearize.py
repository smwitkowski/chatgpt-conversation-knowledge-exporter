"""Linearize ChatGPT conversation export into ordered message list."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ck_exporter.export_schema import (
    get_current_node,
    get_mapping,
    get_message_create_time,
    get_message_id,
    get_message_parts,
    get_message_role,
    get_title,
)
from ck_exporter.input_normalize import load_conversations

console = Console()


def linearize_conversation(conversation: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Linearize a single conversation by walking the current_node path.

    Returns a list of messages with role, text, timestamps, and IDs.
    """
    mapping = get_mapping(conversation)
    current = get_current_node(conversation)

    if not current:
        return []

    # Walk parent chain to root
    path = []
    node_id = current
    visited = set()

    while node_id and node_id not in visited:
        visited.add(node_id)
        path.append(node_id)
        node = mapping.get(node_id, {})
        node_id = node.get("parent")

    # Reverse to get chronological order
    path.reverse()

    # Extract messages
    messages = []
    for node_id in path:
        node = mapping.get(node_id, {})
        message = node.get("message")
        if not message:
            continue

        role = get_message_role(message)
        parts = get_message_parts(message)
        text = "\n".join(parts).strip()

        if not text or not role:
            continue

        create_time = get_message_create_time(message)
        message_id = get_message_id(message)

        messages.append({
            "id": message_id,
            "role": role,
            "create_time": create_time,
            "time_iso": datetime.fromtimestamp(create_time).isoformat() if create_time else None,
            "text": text,
        })

    return messages


def write_conversation_markdown(
    messages: List[Dict[str, Any]],
    conversation_id: str,
    title: str,
    output_dir: Path,
) -> Path:
    """Write linearized messages to markdown file."""
    output_path = output_dir / conversation_id / "conversation.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(f"Conversation ID: `{conversation_id}`\n\n")
        f.write("---\n\n")

        for msg in messages:
            role = msg["role"]
            text = msg["text"]
            time_iso = msg.get("time_iso", "")
            msg_id = msg.get("id", "")

            f.write(f"## {role.title()}\n\n")
            if time_iso:
                f.write(f"**Time**: {time_iso}\n\n")
            if msg_id:
                f.write(f"**Message ID**: `{msg_id}`\n\n")
            f.write(f"{text}\n\n")
            f.write("---\n\n")

    return output_path


def linearize_export(input_path: Path, output_dir: Path) -> None:
    """
    Process ChatGPT export JSON and write linearized conversations.

    Accepts either:
    - A top-level list of conversations (standard export format)
    - A single conversation object with mapping/current_node
    """
    console.print(f"[bold]Loading export from[/bold] {input_path}")

    conversations = load_conversations(input_path)

    console.print(f"[green]Found {len(conversations)} conversations[/green]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Linearizing conversations...", total=len(conversations))

        for conv in conversations:
            conv_id = conv.get("id") or conv.get("conversation_id")
            if not conv_id:
                console.print("[yellow]Skipping conversation without ID[/yellow]")
                progress.advance(task)
                continue

            title = get_title(conv)
            messages = linearize_conversation(conv)

            if messages:
                output_path = write_conversation_markdown(messages, conv_id, title, output_dir)
                console.print(f"[dim]  → {conv_id}: {len(messages)} messages → {output_path}[/dim]")
            else:
                console.print(f"[yellow]  → {conv_id}: No messages found[/yellow]")

            progress.advance(task)

    console.print(f"[bold green]✓ Linearization complete[/bold green]")
