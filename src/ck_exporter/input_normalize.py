"""Input normalization for ChatGPT conversation exports.

Supports:
- Standard export format: top-level list of conversations
- Single conversation format: top-level dict with mapping/current_node
- Claude export format: top-level dict with platform="CLAUDE_AI" and chat_messages[]
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, List


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
    chat_messages = claude_conv.get("chat_messages", [])
    if not chat_messages:
        # Empty conversation - return minimal structure
        return {
            "conversation_id": claude_conv.get("uuid", "unknown"),
            "title": claude_conv.get("name") or "Untitled Conversation",
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
                    "parts": [msg.get("text", "")],
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
        "mapping": mapping,
        "current_node": current_node,
    }


def load_conversations(input_path: Path) -> List[dict]:
    """
    Load and normalize conversations from JSON file.

    Supports:
    - List of conversations (standard ChatGPT export format)
    - Single ChatGPT conversation dict (with mapping/current_node)
    - Claude conversation export (with platform="CLAUDE_AI" and chat_messages[])

    For single ChatGPT conversations missing id/conversation_id, injects conversation_id
    based on filename stem.

    Raises ValueError if input format is not recognized.
    """
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Case 1: Already a list (standard export format)
    if isinstance(data, list):
        return data

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

