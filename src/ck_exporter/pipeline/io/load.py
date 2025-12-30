"""Input normalization for ChatGPT conversation exports.

Supports:
- Standard export format: top-level list of conversations
- Single conversation format: top-level dict with mapping/current_node
- Claude export format: top-level dict with platform="CLAUDE_AI" and chat_messages[]
- Directory inputs: a folder containing many per-conversation JSON files (e.g. chatgpt-conversations/)
- Meeting artifacts: Markdown (.md) and plain text (.txt) meeting notes and transcripts
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional

from ck_exporter.pipeline.io.meeting_notes import (
    is_meeting_artifact,
    parse_markdown_meeting,
    parse_text_transcript,
)


def is_chatgpt_single_conversation(obj: Any) -> bool:
    """Check if object is a ChatGPT-style single conversation."""
    if not isinstance(obj, dict):
        return False
    return "mapping" in obj and "current_node" in obj


def is_claude_conversation(obj: Any) -> bool:
    """Check if object is a Claude AI conversation export."""
    if not isinstance(obj, dict):
        return False
    return obj.get("platform") == "CLAUDE_AI" and isinstance(obj.get("chat_messages"), list)


def parse_iso_timestamp(iso_str: str) -> float | None:
    """Parse ISO timestamp string to epoch seconds float."""
    if not iso_str:
        return None
    try:
        # Handle ISO format with timezone (e.g., "2025-12-18T18:06:43.449478+00:00")
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.timestamp()
    except (ValueError, AttributeError):
        return None


def convert_claude_to_chatgpt(claude_conv: dict) -> dict:
    """
    Convert Claude conversation export to ChatGPT-style conversation dict.

    Creates a synthetic mapping/current_node structure that works with existing
    linearization logic.
    """
    # Preserve Claude "project" metadata when available (used by topic pipeline).
    # In observed exports this is present as:
    # - top-level "project_uuid"
    # - and/or nested "project": {"uuid": "...", "name": "..."}
    project_id = claude_conv.get("project_uuid")
    project = claude_conv.get("project")
    if not project_id and isinstance(project, dict):
        project_id = project.get("uuid")
    project_name = project.get("name") if isinstance(project, dict) else None

    chat_messages = claude_conv.get("chat_messages", [])
    if not chat_messages:
        # Empty conversation - return minimal structure
        return {
            "conversation_id": claude_conv.get("uuid", "unknown"),
            "title": claude_conv.get("name") or "Untitled Conversation",
            "project_id": project_id,
            "project_name": project_name,
            "mapping": {},
            "current_node": None,
        }

    # Build mapping: one node per message
    mapping = {}
    previous_uuid = None

    for msg in chat_messages:
        msg_uuid = msg.get("uuid")
        if not msg_uuid:
            continue  # Skip messages without UUID

        # Map sender to role
        sender = msg.get("sender", "").lower()
        if sender == "human":
            role = "user"
        elif sender == "assistant":
            role = "assistant"
        else:
            role = "system"  # Unknown sender types -> system

        # Parse timestamp
        created_at = msg.get("created_at")
        create_time = parse_iso_timestamp(created_at) if created_at else None

        # Extract text from either 'text' field or 'content' array
        text = msg.get("text", "")
        if not text and "content" in msg:
            # Newer Claude export format: content is an array of objects with 'text' field
            content_items = msg.get("content", [])
            if isinstance(content_items, list):
                text_parts = [item.get("text", "") for item in content_items if isinstance(item, dict)]
                text = "\n".join(text_parts).strip()

        # Build message node
        mapping[msg_uuid] = {
            "id": msg_uuid,
            "parent": previous_uuid,
            "message": {
                "id": msg_uuid,
                "author": {
                    "role": role,
                    "name": None,
                    "metadata": {},
                },
                "create_time": create_time,
                "update_time": None,
                "content": {
                    "content_type": "text",
                    "parts": [text],
                },
                "status": "finished_successfully",
                "end_turn": True,
                "weight": 1,
                "metadata": {},
                "recipient": "all",
                "channel": None,
            },
        }

        previous_uuid = msg_uuid

    # Current node is the last message UUID
    current_node = previous_uuid if previous_uuid else None

    return {
        "conversation_id": claude_conv.get("uuid", "unknown"),
        "title": claude_conv.get("name") or "Untitled Conversation",
        "project_id": project_id,
        "project_name": project_name,
        "mapping": mapping,
        "current_node": current_node,
    }


def _list_input_files(input_dir: Path) -> list[Path]:
    """
    List input files in a directory (recursively), sorted for determinism.

    Supports JSON, Markdown (.md), and text (.txt) files.
    This is used to support inputs like `chatgpt-conversations/` or `meeting_artifacts/`.

    Returns:
        Sorted list of file paths
    """
    # Collect all supported file types
    all_files = []
    # Prefer direct children first (common case), then fall back to recursive search.
    for ext in [".json", ".md", ".txt"]:
        direct = sorted(p for p in input_dir.glob(f"*{ext}") if p.is_file())
        if direct:
            all_files.extend(direct)
        else:
            all_files.extend(sorted(p for p in input_dir.rglob(f"*{ext}") if p.is_file()))
    
    # Sort all files together for deterministic ordering
    return sorted(set(all_files))


def _list_json_files(input_dir: Path) -> list[Path]:
    """
    List JSON files in a directory (recursively), sorted for determinism.

    This is a legacy function kept for backward compatibility.
    Use _list_input_files() for new code that needs to support multiple file types.
    """
    # Prefer direct children first (common case), then fall back to recursive search.
    direct = sorted(p for p in input_dir.glob("*.json") if p.is_file())
    if direct:
        return direct
    return sorted(p for p in input_dir.rglob("*.json") if p.is_file())


def _load_conversations_file(input_path: Path) -> List[dict]:
    """
    Load and normalize conversations from a single file.

    Supports:
    - JSON files:
      - List of conversations (standard ChatGPT export format)
      - Single ChatGPT conversation dict (with mapping/current_node)
      - Claude conversation export (with platform="CLAUDE_AI" and chat_messages[])
    - Markdown files (.md): Meeting notes with notes and transcript sections
    - Text files (.txt): Plain text transcripts with timestamped lines

    For single ChatGPT conversations missing id/conversation_id, injects conversation_id
    based on filename stem.

    Raises ValueError if input format is not recognized.
    """
    # Handle meeting artifacts (Markdown and text files)
    if is_meeting_artifact(input_path):
        if input_path.suffix.lower() == ".md":
            return [parse_markdown_meeting(input_path)]
        elif input_path.suffix.lower() == ".txt":
            return [parse_text_transcript(input_path)]
        else:
            raise ValueError(f"Unsupported meeting artifact format: {input_path.suffix}")

    # Handle JSON files (existing logic)
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Case 1: Already a list (standard export format OR list of Claude exports)
    if isinstance(data, list):
        normalized: List[dict] = []
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                continue

            # Convert Claude exports even when embedded in a list
            if is_claude_conversation(item):
                normalized.append(convert_claude_to_chatgpt(item))
                continue

            # If it's a single ChatGPT conversation object, ensure it has an ID
            if is_chatgpt_single_conversation(item):
                if not item.get("id") and not item.get("conversation_id"):
                    # Prefer Claude-style uuid if present; otherwise fall back to index-based ID
                    item["conversation_id"] = item.get("uuid") or f"{input_path.stem}_{i}"
                normalized.append(item)
                continue

            # Otherwise, include as-is (downstream may skip if no ID)
            normalized.append(item)

        return normalized

    # Case 2: Claude conversation export
    if is_claude_conversation(data):
        converted = convert_claude_to_chatgpt(data)
        return [converted]

    # Case 3: Single ChatGPT conversation dict
    if is_chatgpt_single_conversation(data):
        # Ensure conversation_id exists
        if not data.get("id") and not data.get("conversation_id"):
            # Use filename stem as conversation_id
            conversation_id = input_path.stem
            data["conversation_id"] = conversation_id
        return [data]

    # Case 4: Unrecognized format
    raise ValueError(
        "Unsupported input format. Expected one of:\n"
        "  - A list of conversations (standard ChatGPT export), or\n"
        "  - A single ChatGPT conversation object with 'mapping' and 'current_node' fields, or\n"
        "  - A Claude conversation export with 'platform'='CLAUDE_AI' and 'chat_messages' array.\n"
        f"Got: {type(data).__name__} with keys: {list(data.keys())[:10] if isinstance(data, dict) else 'N/A'}"
    )


def load_conversations(input_path: Path, limit: Optional[int] = None) -> List[dict]:
    """
    Load and normalize conversations from a file OR directory.

    Supports:
    - JSON files:
      - List of conversations (standard ChatGPT export format)
      - Single ChatGPT conversation dict (with mapping/current_node)
      - Claude conversation export (with platform="CLAUDE_AI" and chat_messages[])
    - Markdown files (.md): Meeting notes with notes and transcript sections
    - Text files (.txt): Plain text transcripts with timestamped lines
    - A directory containing many files of the above types
      (common for per-conversation exports like `chatgpt-conversations/` or `meeting_artifacts/`)

    For single ChatGPT conversations missing id/conversation_id, injects conversation_id
    based on filename stem.

    Args:
        input_path: Path to file or directory containing supported files
        limit: Optional limit on number of conversations to return. For directories,
               selects first N files by sorted filename (deterministic). For list exports,
               returns first N conversations after normalization.

    Raises ValueError if input format is not recognized or no supported files found.
    """
    if input_path.is_dir():
        input_files = _list_input_files(input_path)
        if not input_files:
            raise ValueError(
                f"No supported files (.json, .md, .txt) found in directory: {input_path}"
            )

        conversations: List[dict] = []
        for p in input_files:
            # Stop if we've reached the limit
            if limit is not None and len(conversations) >= limit:
                break

            # Be liberal in what we accept: skip files that aren't a supported conversation format.
            try:
                file_conversations = _load_conversations_file(p)
                conversations.extend(file_conversations)

                # If limit is set and we've exceeded it, trim to limit
                if limit is not None and len(conversations) > limit:
                    conversations = conversations[:limit]
                    break
            except ValueError:
                continue
        return conversations

    # For single file inputs, load and optionally limit
    conversations = _load_conversations_file(input_path)
    if limit is not None:
        return conversations[:limit]
    return conversations
