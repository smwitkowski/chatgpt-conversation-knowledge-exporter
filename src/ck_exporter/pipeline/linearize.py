"""Linearize ChatGPT conversation export into ordered message list."""

from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ck_exporter.logging import get_logger, should_show_progress, with_context
from ck_exporter.pipeline.io import (
    get_current_node,
    get_mapping,
    get_message_create_time,
    get_message_id,
    get_message_parts,
    get_message_role,
    get_project_id,
    get_project_name,
    get_title,
    load_conversations,
)

logger = get_logger(__name__)


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
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
) -> Path:
    """Write linearized messages to markdown file."""
    output_path = output_dir / conversation_id / "conversation.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(f"Conversation ID: `{conversation_id}`\n\n")
        if project_name and project_id:
            f.write(f"Project: **{project_name}** (`{project_id}`)\n\n")
        elif project_name:
            f.write(f"Project: **{project_name}**\n\n")
        elif project_id:
            f.write(f"Project ID: `{project_id}`\n\n")
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


def linearize_export(
    input_path: Path,
    output_dir: Path,
    limit: Optional[int] = None,
    progress_cb: Optional[Callable[[int, int, Optional[dict]], None]] = None,
) -> None:
    """
    Process ChatGPT/Claude exports (or per-conversation directories) and write linearized conversations.

    Accepts either:
    - A top-level list of conversations (standard export format)
    - A single conversation object with mapping/current_node
    - A directory containing many per-conversation `.json` files

    Args:
        input_path: Path to JSON file or directory containing JSON files
        output_dir: Output directory for linearized markdown files
        limit: Optional limit on number of conversations to process
        progress_cb: Optional callback(completed, total, context) for progress updates
    """
    logger.info(
        "Loading export",
        extra={
            "event": "linearize.export.load",
            "input_path": str(input_path),
            "limit": limit,
        },
    )

    conversations = load_conversations(input_path, limit=limit)

    logger.info(
        "Found conversations",
        extra={"event": "linearize.export.found", "num_conversations": len(conversations)},
    )

    # Notify progress callback of total
    if progress_cb:
        progress_cb(0, len(conversations), {})

    if should_show_progress() and not progress_cb:
        console = Console(stderr=True)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Linearizing conversations...", total=len(conversations))

            for conv in conversations:
                conv_id = conv.get("id") or conv.get("conversation_id")
                if not conv_id:
                    logger.warning(
                        "Skipping conversation without ID",
                        extra={"event": "linearize.conversation.skipped", "reason": "no_id"},
                    )
                    progress.advance(task)
                    continue

                conv_logger = with_context(logger, conversation_id=conv_id)
                title = get_title(conv)
                project_id = get_project_id(conv)
                project_name = get_project_name(conv)
                messages = linearize_conversation(conv)

                if messages:
                    output_path = write_conversation_markdown(
                        messages,
                        conv_id,
                        title,
                        output_dir,
                        project_id=project_id,
                        project_name=project_name,
                    )
                    conv_logger.debug(
                        "Linearized conversation",
                        extra={
                            "event": "linearize.conversation.complete",
                            "num_messages": len(messages),
                            "output_path": str(output_path),
                        },
                    )
                else:
                    conv_logger.warning(
                        "No messages found",
                        extra={"event": "linearize.conversation.skipped", "reason": "no_messages"},
                    )

                progress.advance(task)
                # Update progress callback if provided
                if progress_cb:
                    progress_cb(progress.tasks[task].completed, len(conversations), {"conversation_id": conv_id})
    else:
        # Non-interactive mode or dashboard mode: process without progress bar
        completed = 0
        for conv in conversations:
            conv_id = conv.get("id") or conv.get("conversation_id")
            if not conv_id:
                logger.warning(
                    "Skipping conversation without ID",
                    extra={"event": "linearize.conversation.skipped", "reason": "no_id"},
                )
                continue

            conv_logger = with_context(logger, conversation_id=conv_id)
            title = get_title(conv)
            project_id = get_project_id(conv)
            project_name = get_project_name(conv)
            messages = linearize_conversation(conv)

            if messages:
                output_path = write_conversation_markdown(
                    messages,
                    conv_id,
                    title,
                    output_dir,
                    project_id=project_id,
                    project_name=project_name,
                )
                conv_logger.debug(
                    "Linearized conversation",
                    extra={
                        "event": "linearize.conversation.complete",
                        "num_messages": len(messages),
                        "output_path": str(output_path),
                    },
                )
            else:
                conv_logger.warning(
                    "No messages found",
                    extra={"event": "linearize.conversation.skipped", "reason": "no_messages"},
                )

            # Update progress callback
            completed += 1
            if progress_cb:
                progress_cb(completed, len(conversations), {"conversation_id": conv_id})

    logger.info(
        "Linearization complete",
        extra={"event": "linearize.export.complete"},
    )
