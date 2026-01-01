"""Convert legacy atom formats to Universal Atom (v2) format."""

from datetime import datetime
from typing import Any, Dict, List

from ck_exporter.core.models.atoms import Atom, Evidence


def convert_facts_to_universal(facts: List[Dict[str, Any]], conversation_id: str) -> List[Dict[str, Any]]:
    """Convert legacy fact atoms to Universal Atom format."""
    universal_atoms = []
    for fact in facts:
        # Map legacy type to kind
        legacy_type = fact.get("type", "fact")
        kind_map = {
            "fact": "fact",
            "definition": "fact",  # definitions are facts
            "requirement": "fact",  # requirements are facts
            "metric": "fact",
            "assumption": "fact",
            "constraint": "fact",
            "idea": "fact",
        }
        kind = kind_map.get(legacy_type, "fact")

        # Convert evidence
        evidence_list = []
        for ev in fact.get("evidence", []):
            evidence_list.append(
                Evidence(
                    message_id=ev.get("message_id"),
                    time_iso=ev.get("time_iso"),
                    text_snippet=ev.get("text_snippet"),
                    conversation_id=ev.get("conversation_id") or conversation_id,
                ).model_dump()
            )

        atom = Atom(
            schema_version=2,
            kind=kind,
            statement=fact.get("statement", ""),
            topic=fact.get("topic", ""),
            status=fact.get("status", "active"),
            status_confidence=None,  # Legacy facts don't have confidence
            evidence=evidence_list,
            extracted_at=fact.get("extracted_at", datetime.now().isoformat()),
            meta={
                "legacy": {
                    "type": legacy_type,  # Preserve original type in meta
                },
            },
        )
        universal_atoms.append(atom.model_dump())
    return universal_atoms


def convert_decisions_to_universal(decisions: List[Dict[str, Any]], conversation_id: str) -> List[Dict[str, Any]]:
    """Convert legacy decision atoms to Universal Atom format."""
    universal_atoms = []
    for decision in decisions:
        # Convert evidence
        evidence_list = []
        for ev in decision.get("evidence", []):
            evidence_list.append(
                Evidence(
                    message_id=ev.get("message_id"),
                    time_iso=ev.get("time_iso"),
                    text_snippet=ev.get("text_snippet"),
                    conversation_id=ev.get("conversation_id") or conversation_id,
                ).model_dump()
            )

        atom = Atom(
            schema_version=2,
            kind="decision",
            statement=decision.get("statement", ""),
            topic=decision.get("topic", ""),
            status=decision.get("status", "active"),
            status_confidence=None,
            evidence=evidence_list,
            extracted_at=decision.get("extracted_at", datetime.now().isoformat()),
            meta={
                "decision": {
                    "alternatives": decision.get("alternatives", []),
                    "rationale": decision.get("rationale"),
                    "consequences": decision.get("consequences"),
                },
            },
        )
        universal_atoms.append(atom.model_dump())
    return universal_atoms


def convert_open_questions_to_universal(questions: List[Dict[str, Any]], conversation_id: str) -> List[Dict[str, Any]]:
    """Convert legacy open question atoms to Universal Atom format."""
    universal_atoms = []
    for question in questions:
        # Convert evidence
        evidence_list = []
        for ev in question.get("evidence", []):
            evidence_list.append(
                Evidence(
                    message_id=ev.get("message_id"),
                    time_iso=ev.get("time_iso"),
                    text_snippet=ev.get("text_snippet"),
                    conversation_id=ev.get("conversation_id") or conversation_id,
                ).model_dump()
            )

        atom = Atom(
            schema_version=2,
            kind="open_question",
            statement=question.get("question", ""),  # question text goes in statement
            topic=question.get("topic", ""),
            status="active",  # Questions are active by default
            status_confidence=None,
            evidence=evidence_list,
            extracted_at=question.get("extracted_at", datetime.now().isoformat()),
            meta={
                "question": {
                    "context": question.get("context"),
                },
            },
        )
        universal_atoms.append(atom.model_dump())
    return universal_atoms


def convert_action_items_to_universal(action_items: List[Dict[str, Any]], conversation_id: str) -> List[Dict[str, Any]]:
    """Convert legacy action item atoms to Universal Atom format."""
    universal_atoms = []
    for ai in action_items:
        # Convert evidence
        evidence_list = []
        for ev in ai.get("evidence", []):
            evidence_list.append(
                Evidence(
                    message_id=ev.get("message_id"),
                    time_iso=ev.get("time_iso"),
                    text_snippet=ev.get("text_snippet"),
                    conversation_id=ev.get("conversation_id") or conversation_id,
                ).model_dump()
            )

        atom = Atom(
            schema_version=2,
            kind="action_item",
            statement=ai.get("statement", ""),
            topic=None,  # Action items don't have topics
            status="open",  # Default to open
            status_confidence=None,
            evidence=evidence_list,
            extracted_at=ai.get("extracted_at", datetime.now().isoformat()),
            meta={
                "task": {
                    # owner, due can be added later via DSPy extraction
                },
            },
        )
        universal_atoms.append(atom.model_dump())
    return universal_atoms

