"""Utilities for deduplicating and compacting atom candidates before Pass 2 refinement."""

import os
from typing import Any


def normalize_statement(text: str) -> str:
    """
    Normalize a statement/question for deduplication.

    Args:
        text: Statement or question text

    Returns:
        Normalized string (lowercase, stripped, basic whitespace normalization)
    """
    return " ".join(text.lower().strip().split())


def deduplicate_candidates(
    all_candidates: dict[str, list[dict[str, Any]]],
    max_evidence_per_item: int | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """
    Deduplicate candidate atoms before Pass 2 refinement.

    This reduces the payload size sent to the LLM and improves throughput.

    Args:
        all_candidates: Dict with "facts", "decisions", "open_questions" lists
        max_evidence_per_item: Optional cap on evidence count per item (None = no cap)

    Returns:
        Deduplicated candidates dict with same structure
    """
    # Get evidence cap from env or use provided default
    if max_evidence_per_item is None:
        max_evidence_per_item = int(os.getenv("CKX_MAX_EVIDENCE_PER_ITEM", "0")) or None

    result = {"facts": [], "decisions": [], "open_questions": []}

    # Deduplicate facts
    seen_facts: dict[tuple[str, str, str], dict[str, Any]] = {}
    for fact in all_candidates.get("facts", []):
        key = (
            fact.get("type", ""),
            fact.get("topic", ""),
            normalize_statement(fact.get("statement", "")),
        )
        if key in seen_facts:
            # Merge evidence arrays
            existing_evidence = seen_facts[key].get("evidence", [])
            new_evidence = fact.get("evidence", [])
            # Deduplicate evidence by message_id
            evidence_map = {ev.get("message_id"): ev for ev in existing_evidence}
            for ev in new_evidence:
                msg_id = ev.get("message_id")
                if msg_id and msg_id not in evidence_map:
                    evidence_map[msg_id] = ev
            merged_evidence = list(evidence_map.values())
            # Apply evidence cap if configured
            if max_evidence_per_item and len(merged_evidence) > max_evidence_per_item:
                merged_evidence = merged_evidence[:max_evidence_per_item]
            seen_facts[key]["evidence"] = merged_evidence
        else:
            # Apply evidence cap if configured
            evidence = fact.get("evidence", [])
            if max_evidence_per_item and len(evidence) > max_evidence_per_item:
                fact = {**fact, "evidence": evidence[:max_evidence_per_item]}
            seen_facts[key] = fact
    result["facts"] = list(seen_facts.values())

    # Deduplicate decisions
    seen_decisions: dict[tuple[str, str, str], dict[str, Any]] = {}
    for decision in all_candidates.get("decisions", []):
        key = (
            decision.get("type", ""),
            decision.get("topic", ""),
            normalize_statement(decision.get("statement", "")),
        )
        if key in seen_decisions:
            # Merge evidence arrays
            existing_evidence = seen_decisions[key].get("evidence", [])
            new_evidence = decision.get("evidence", [])
            evidence_map = {ev.get("message_id"): ev for ev in existing_evidence}
            for ev in new_evidence:
                msg_id = ev.get("message_id")
                if msg_id and msg_id not in evidence_map:
                    evidence_map[msg_id] = ev
            merged_evidence = list(evidence_map.values())
            if max_evidence_per_item and len(merged_evidence) > max_evidence_per_item:
                merged_evidence = merged_evidence[:max_evidence_per_item]
            seen_decisions[key]["evidence"] = merged_evidence
        else:
            evidence = decision.get("evidence", [])
            if max_evidence_per_item and len(evidence) > max_evidence_per_item:
                decision = {**decision, "evidence": evidence[:max_evidence_per_item]}
            seen_decisions[key] = decision
    result["decisions"] = list(seen_decisions.values())

    # Deduplicate open questions
    seen_questions: dict[tuple[str, str], dict[str, Any]] = {}
    for question in all_candidates.get("open_questions", []):
        key = (
            question.get("topic", ""),
            normalize_statement(question.get("question", "")),
        )
        if key in seen_questions:
            # Merge evidence arrays
            existing_evidence = seen_questions[key].get("evidence", [])
            new_evidence = question.get("evidence", [])
            evidence_map = {ev.get("message_id"): ev for ev in existing_evidence}
            for ev in new_evidence:
                msg_id = ev.get("message_id")
                if msg_id and msg_id not in evidence_map:
                    evidence_map[msg_id] = ev
            merged_evidence = list(evidence_map.values())
            if max_evidence_per_item and len(merged_evidence) > max_evidence_per_item:
                merged_evidence = merged_evidence[:max_evidence_per_item]
            seen_questions[key]["evidence"] = merged_evidence
        else:
            evidence = question.get("evidence", [])
            if max_evidence_per_item and len(evidence) > max_evidence_per_item:
                question = {**question, "evidence": evidence[:max_evidence_per_item]}
            seen_questions[key] = question
    result["open_questions"] = list(seen_questions.values())

    return result
