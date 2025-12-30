"""JSON extraction and repair utilities."""

import json
from typing import Any, Optional


def extract_json_from_text(text: str) -> Optional[dict[str, Any]]:
    """
    Try to extract JSON from text that might have markdown code blocks.

    Args:
        text: Text that may contain JSON (possibly wrapped in markdown)

    Returns:
        Parsed JSON dict, or None if parsing fails
    """
    text = text.strip()
    # Try to find JSON in markdown code blocks
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        if end > start:
            text = text[start:end].strip()
    elif "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        if end > start:
            text = text[start:end].strip()
    # Try parsing
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None
