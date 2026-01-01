"""Action item extraction from meeting notes.

Extracts action items deterministically from Google Meet markdown notes
by parsing checklist items in system message sections.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from ck_exporter.core.models.atoms import ActionItem, Evidence


def extract_action_items_from_conversation(
    conversation: Dict[str, Any],
    conversation_id: str,
) -> List[Dict[str, Any]]:
    """
    Extract action items from a conversation (meeting notes).

    Looks for checklist items (`- [ ] ...`) in system messages (notes sections)
    that contain action-item-related headings.

    Args:
        conversation: Conversation dict with mapping/current_node structure
        conversation_id: Conversation ID for evidence pointers

    Returns:
        List of action item dicts (ready for JSONL serialization)
    """
    action_items = []

    # Get the mapping structure
    mapping = conversation.get("mapping", {})
    if not mapping:
        return action_items

    # Iterate through all messages
    for node_id, node in mapping.items():
        message = node.get("message")
        if not message or not isinstance(message, dict):
            continue
        
        author = message.get("author", {})
        role = author.get("role", "")

        # Only process system messages (notes sections)
        if role != "system":
            continue

        message_id = message.get("id", "")
        content = message.get("content", {})
        parts = content.get("parts", [])

        if not parts:
            continue

        # Combine all parts into a single text
        text = "\n".join(parts)

        # Check if this is an action items section
        # Look for headings that suggest action items
        heading_match = re.search(r'^#+\s+(.+)$', text, re.MULTILINE)
        has_action_heading = False
        if heading_match:
            heading = heading_match.group(1).lower()
            has_action_heading = any(keyword in heading for keyword in ["next steps", "action", "todo", "tasks"])

        # Extract checklist items
        # Extract from sections with action-item headings, or from any system message with checklists
        checklist_pattern = r'^-\s+\[([ x])\]\s+(.+)$'
        for line in text.split('\n'):
            match = re.match(checklist_pattern, line.strip())
            if match:
                checked = match.group(1) == 'x'
                statement = match.group(2).strip()

                # Skip empty statements
                if not statement:
                    continue

                # Extract if this section has action-item heading, or if it's any system message with checklists
                # (permissive: extract from any system message that contains checklists)
                if has_action_heading or True:  # Extract from any system message with checklists
                    # Create evidence pointer
                    evidence = [
                        Evidence(
                            message_id=message_id,
                            time_iso=None,  # No absolute time for v1
                            text_snippet=statement[:200],  # Truncate snippet
                        ).model_dump()
                    ]

                    # Create action item
                    action_item = ActionItem(
                        statement=statement,
                        evidence=evidence,
                        extracted_at=datetime.now().isoformat(),
                    )

                    action_items.append(action_item.model_dump())

    return action_items

