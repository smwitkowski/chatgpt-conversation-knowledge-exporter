"""Tests for action item extraction from meeting notes."""

from pathlib import Path

import pytest

from ck_exporter.pipeline.action_items import extract_action_items_from_conversation


def test_extract_action_items_from_checklist():
    """Test extracting action items from a checklist in a notes section."""
    conversation = {
        "mapping": {
            "notes:next-steps": {
                "id": "notes:next-steps",
                "parent": None,
                "message": {
                    "id": "notes:next-steps",
                    "author": {
                        "role": "system",
                        "name": None,
                        "metadata": {},
                    },
                    "content": {
                        "content_type": "text",
                        "parts": [
                            "### Suggested next steps\n\n- [ ] Daniel Baranski will schedule a meeting Monday or Tuesday to work on connectivity for int.\n- [ ] Igor Baytler will send TNS names to a single node.\n- [x] Jason Perry will set up NATs and provide IP addresses.",
                        ],
                    },
                },
            },
        },
        "current_node": "notes:next-steps",
    }

    action_items = extract_action_items_from_conversation(conversation, "test-conv-1")

    assert len(action_items) == 3
    assert action_items[0]["statement"] == "Daniel Baranski will schedule a meeting Monday or Tuesday to work on connectivity for int."
    assert action_items[1]["statement"] == "Igor Baytler will send TNS names to a single node."
    assert action_items[2]["statement"] == "Jason Perry will set up NATs and provide IP addresses."

    # Check evidence pointers
    assert action_items[0]["evidence"][0]["message_id"] == "notes:next-steps"
    assert action_items[1]["evidence"][0]["message_id"] == "notes:next-steps"


def test_extract_action_items_no_checklist():
    """Test that non-checklist sections don't produce action items."""
    conversation = {
        "mapping": {
            "notes:summary": {
                "id": "notes:summary",
                "parent": None,
                "message": {
                    "id": "notes:summary",
                    "author": {
                        "role": "system",
                        "name": None,
                        "metadata": {},
                    },
                    "content": {
                        "content_type": "text",
                        "parts": [
                            "### Summary\n\nThis is a regular summary without checklists.",
                        ],
                    },
                },
            },
        },
        "current_node": "notes:summary",
    }

    action_items = extract_action_items_from_conversation(conversation, "test-conv-2")
    assert len(action_items) == 0


def test_extract_action_items_empty_conversation():
    """Test that empty conversations produce no action items."""
    conversation = {
        "mapping": {},
        "current_node": None,
    }

    action_items = extract_action_items_from_conversation(conversation, "test-conv-3")
    assert len(action_items) == 0


def test_extract_action_items_user_messages_ignored():
    """Test that user messages (transcript) are ignored."""
    conversation = {
        "mapping": {
            "00:01:30": {
                "id": "00:01:30",
                "parent": None,
                "message": {
                    "id": "00:01:30",
                    "author": {
                        "role": "user",
                        "name": None,
                        "metadata": {},
                    },
                    "content": {
                        "content_type": "text",
                        "parts": [
                            "- [ ] This should be ignored",
                        ],
                    },
                },
            },
        },
        "current_node": "00:01:30",
    }

    action_items = extract_action_items_from_conversation(conversation, "test-conv-4")
    assert len(action_items) == 0


def test_extract_action_items_multiple_sections():
    """Test extracting from multiple action item sections."""
    conversation = {
        "mapping": {
            "notes:action-items": {
                "id": "notes:action-items",
                "parent": None,
                "message": {
                    "id": "notes:action-items",
                    "author": {
                        "role": "system",
                        "name": None,
                        "metadata": {},
                    },
                    "content": {
                        "content_type": "text",
                        "parts": [
                            "### Action Items\n\n- [ ] Task 1\n- [ ] Task 2",
                        ],
                    },
                },
            },
            "notes:next-steps": {
                "id": "notes:next-steps",
                "parent": "notes:action-items",
                "message": {
                    "id": "notes:next-steps",
                    "author": {
                        "role": "system",
                        "name": None,
                        "metadata": {},
                    },
                    "content": {
                        "content_type": "text",
                        "parts": [
                            "### Next Steps\n\n- [ ] Task 3",
                        ],
                    },
                },
            },
        },
        "current_node": "notes:next-steps",
    }

    action_items = extract_action_items_from_conversation(conversation, "test-conv-5")
    assert len(action_items) == 3
    assert action_items[0]["statement"] == "Task 1"
    assert action_items[1]["statement"] == "Task 2"
    assert action_items[2]["statement"] == "Task 3"

