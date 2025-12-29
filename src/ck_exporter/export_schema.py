"""Schema helpers for ChatGPT export JSON structure."""

from typing import Any, Dict, List, Optional


def get_conversation_id(conversation: Dict[str, Any]) -> Optional[str]:
    """Extract conversation ID from a conversation dict."""
    return conversation.get("id") or conversation.get("conversation_id")


def get_current_node(conversation: Dict[str, Any]) -> Optional[str]:
    """Get the current node ID from a conversation."""
    return conversation.get("current_node")


def get_mapping(conversation: Dict[str, Any]) -> Dict[str, Any]:
    """Get the mapping dict from a conversation."""
    return conversation.get("mapping", {})


def get_title(conversation: Dict[str, Any]) -> str:
    """Get conversation title, with fallback."""
    return conversation.get("title") or "Untitled Conversation"


def get_message_role(message: Dict[str, Any]) -> Optional[str]:
    """Extract role from a message dict."""
    author = message.get("author", {})
    if isinstance(author, dict):
        return author.get("role")
    return None


def get_message_parts(message: Dict[str, Any]) -> List[str]:
    """Extract text parts from a message content."""
    content = message.get("content", {})
    if isinstance(content, dict):
        parts = content.get("parts", [])
        if isinstance(parts, list):
            return [p for p in parts if isinstance(p, str)]
    return []


def get_message_id(message: Dict[str, Any]) -> Optional[str]:
    """Extract message ID."""
    return message.get("id")


def get_message_create_time(message: Dict[str, Any]) -> Optional[float]:
    """Extract create_time timestamp."""
    return message.get("create_time")
