"""Parse meeting metadata from Google Meet markdown files."""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ck_exporter.pipeline.io.meeting_notes import parse_markdown_meeting


def extract_meeting_metadata(path: Path) -> Dict[str, Any]:
    """
    Extract explicit metadata from Google Meet markdown file.

    Parses:
    - Meeting date (from header)
    - Meeting title
    - Participant emails (from Invited section)
    - Links (transcript, recording, calendar)

    Args:
        path: Path to Markdown meeting file

    Returns:
        Dict with parsed metadata
    """
    content = path.read_text(encoding='utf-8')
    lines = content.split('\n')

    metadata: Dict[str, Any] = {
        "source_system": "google_meet",
        "meeting_date": None,
        "meeting_title": None,
        "participants": [],
        "links": {
            "transcript": None,
            "recording": None,
            "calendar": None,
        },
    }

    # Extract date (usually first line or near top)
    for i, line in enumerate(lines[:10]):
        # Look for date patterns like "Aug 4, 2025" or "2025-08-04"
        date_match = re.search(r'(\w+\s+\d+,\s+\d{4})|(\d{4}-\d{2}-\d{2})', line)
        if date_match:
            try:
                date_str = date_match.group(1) or date_match.group(2)
                # Try parsing common formats
                if ',' in date_str:
                    metadata["meeting_date"] = datetime.strptime(date_str, "%b %d, %Y").isoformat()
                else:
                    metadata["meeting_date"] = datetime.strptime(date_str, "%Y-%m-%d").isoformat()
                break
            except ValueError:
                pass

    # Extract title (first ## heading)
    for line in lines[:30]:
        if line.startswith('## '):
            title = re.sub(r'^##\s+', '', line).strip()
            # Remove markdown links and formatting
            title = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', title)
            metadata["meeting_title"] = title
            break

    # Extract participant emails (from "Invited" section)
    in_invited_section = False
    for line in lines[:50]:
        if 'Invited' in line or 'invited' in line.lower():
            in_invited_section = True
            continue
        if in_invited_section:
            # Look for email patterns
            emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', line)
            metadata["participants"].extend(emails)
            # Stop if we hit a new section (next ##)
            if line.startswith('##'):
                break

    # Extract links
    for line in lines[:50]:
        # Transcript link
        if 'Transcript' in line or 'transcript' in line.lower():
            transcript_match = re.search(r'\[Transcript\]\(([^\)]+)\)', line)
            if transcript_match:
                metadata["links"]["transcript"] = transcript_match.group(1)
        # Recording link
        if 'Recording' in line or 'recording' in line.lower():
            recording_match = re.search(r'\[Recording\]\(([^\)]+)\)', line)
            if recording_match:
                metadata["links"]["recording"] = recording_match.group(1)
        # Calendar link
        if 'calendar' in line.lower() or 'event' in line.lower():
            calendar_match = re.search(r'https://www\.google\.com/calendar/event[^\s\)]+', line)
            if calendar_match:
                metadata["links"]["calendar"] = calendar_match.group(0)

    return metadata


def infer_meeting_kind(metadata: Dict[str, Any], conversation: Dict[str, Any]) -> str:
    """
    Infer meeting kind (internal|client|mixed|unknown) from metadata and content.

    This is a simple heuristic - DSPy will refine this.

    Args:
        metadata: Parsed metadata
        conversation: Conversation dict

    Returns:
        Inferred meeting kind
    """
    participants = metadata.get("participants", [])
    title = metadata.get("meeting_title", "").lower()

    # Check for explicit "internal" in title
    if "internal" in title:
        return "internal"

    # Check participant domains
    domains = set()
    for email in participants:
        if '@' in email:
            domain = email.split('@')[1].lower()
            domains.add(domain)

    # If all participants are from same domain (likely internal)
    if len(domains) <= 1:
        return "internal"

    # If multiple domains, likely client or mixed
    # Simple heuristic: if title mentions client name or project, likely client
    if any(word in title for word in ["client", "wth", "project", "workshop"]):
        return "client"

    return "unknown"

