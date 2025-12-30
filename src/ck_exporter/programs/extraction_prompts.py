"""Prompts for knowledge atom extraction."""

# Pass 1: Fast extraction prompt (for Gemini Flash)
PASS1_EXTRACTION_PROMPT = """You are extracting structured knowledge from a conversation about a project.

Analyze the following conversation chunk and extract:
1. **Facts**: Concrete statements about the project (what it is, how it works, etc.)
2. **Decisions**: Explicit or implicit decisions made (with alternatives and rationale if available)
3. **Open Questions**: Unresolved questions or uncertainties mentioned

For each item, provide:
- type: one of decision|requirement|definition|metric|risk|assumption|constraint|idea|fact
- topic: category (e.g., "pricing", "architecture", "ICP", "content", "evals", "marketing")
- statement: the actual knowledge statement
- status: active|deprecated|uncertain
- evidence: array with message_id and time_iso pointing to source messages

For decisions, also include:
- alternatives: what other options were considered
- rationale: why this decision was made
- consequences: expected outcomes

Return ONLY valid JSON matching this schema (no markdown, no code blocks, just JSON):
{{
  "facts": [
    {{
      "type": "fact|definition|requirement|metric|constraint",
      "topic": "...",
      "statement": "...",
      "status": "active",
      "evidence": [{{"message_id": "...", "time_iso": "..."}}]
    }}
  ],
  "decisions": [
    {{
      "type": "decision",
      "topic": "...",
      "statement": "...",
      "status": "active",
      "alternatives": ["..."],
      "rationale": "...",
      "consequences": "...",
      "evidence": [{{"message_id": "...", "time_iso": "..."}}]
    }}
  ],
  "open_questions": [
    {{
      "question": "...",
      "topic": "...",
      "context": "...",
      "evidence": [{{"message_id": "...", "time_iso": "..."}}]
    }}
  ]
}}

Conversation chunk:
{chunk_text}
"""

# Pass 2: Refinement prompt (for GPT-5.2)
PASS2_REFINEMENT_PROMPT = """You are refining and consolidating knowledge atoms extracted from a conversation.

You have received candidate extractions from multiple chunks of the same conversation. Your task is to:

1. **Deduplicate semantically**: Merge items that express the same knowledge (even if worded differently)
2. **Normalize**: Ensure consistent type/topic/status values
3. **Validate**: Ensure all evidence arrays are properly formatted with message_id and time_iso
4. **Filter**: Remove obviously redundant, low-value, or duplicate items
5. **Refine**: Make wording concise and actionable while preserving meaning

Conversation metadata:
- ID: {conversation_id}
- Title: {conversation_title}

Candidates to refine:
{all_candidates_json}

Return ONLY valid JSON matching this schema (no markdown, no code blocks, just JSON):
{{
  "facts": [
    {{
      "type": "fact|definition|requirement|metric|constraint|risk|assumption|idea",
      "topic": "...",
      "statement": "...",
      "status": "active|deprecated|uncertain",
      "evidence": [{{"message_id": "...", "time_iso": "..."}}]
    }}
  ],
  "decisions": [
    {{
      "type": "decision",
      "topic": "...",
      "statement": "...",
      "status": "active|deprecated|uncertain",
      "alternatives": ["..."],
      "rationale": "...",
      "consequences": "...",
      "evidence": [{{"message_id": "...", "time_iso": "..."}}]
    }}
  ],
  "open_questions": [
    {{
      "question": "...",
      "topic": "...",
      "context": "...",
      "evidence": [{{"message_id": "...", "time_iso": "..."}}]
    }}
  ]
}}
"""
