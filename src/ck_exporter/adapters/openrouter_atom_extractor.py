"""OpenRouter-backed atom extractor adapter."""

import json
from typing import Any

from ck_exporter.core.ports.atom_extractor import AtomExtractor
from ck_exporter.core.ports.llm import LLMClient
from ck_exporter.logging import get_logger
from ck_exporter.programs.extraction_prompts import (
    PASS1_EXTRACTION_PROMPT,
    PASS2_REFINEMENT_PROMPT,
)
from ck_exporter.programs.json_extract import extract_json_from_text
from ck_exporter.utils.atom_candidates import deduplicate_candidates

logger = get_logger(__name__)


class OpenRouterAtomExtractor:
    """OpenRouter-backed implementation of AtomExtractor."""

    def __init__(
        self,
        fast_llm: LLMClient,
        big_llm: LLMClient,
        fast_model: str = "z-ai/glm-4.7",
        big_model: str = "z-ai/glm-4.7",
    ):
        """
        Initialize atom extractor.

        Args:
            fast_llm: LLM client for Pass 1 (fast extraction)
            big_llm: LLM client for Pass 2 (refinement)
            fast_model: Model identifier for Pass 1
            big_model: Model identifier for Pass 2
        """
        self.fast_llm = fast_llm
        self.big_llm = big_llm
        self.fast_model = fast_model
        self.big_model = big_model

    def extract_from_chunk(self, chunk_text: str) -> dict[str, Any]:
        """
        Extract candidate atoms from a conversation chunk (Pass 1).

        Args:
            chunk_text: Formatted conversation chunk text

        Returns:
            Dict with keys: "facts", "decisions", "open_questions"
        """
        prompt = PASS1_EXTRACTION_PROMPT.format(chunk_text=chunk_text)

        try:
            # Try with json_object=True first (structured output reduces repair calls)
            try:
                content = self.fast_llm.chat(
                    model=self.fast_model,
                    system="You are a knowledge extraction assistant. Return only valid JSON, no markdown, no code blocks.",
                    user=prompt,
                    temperature=0.3,
                    json_object=True,
                )
            except Exception as e:
                # If json_object is not supported (e.g., 400 Bad Request), retry without it
                error_str = str(e).lower()
                if "response_format" in error_str or "json_object" in error_str or "400" in error_str:
                    logger.debug(
                        "json_object not supported, falling back to regular mode",
                        extra={"event": "extractor.pass1.json_object_fallback", "error": str(e)},
                    )
                    content = self.fast_llm.chat(
                        model=self.fast_model,
                        system="You are a knowledge extraction assistant. Return only valid JSON, no markdown, no code blocks.",
                        user=prompt,
                        temperature=0.3,
                        json_object=False,
                    )
                else:
                    # Re-raise if it's a different error
                    raise

            if not content:
                return {"facts": [], "decisions": [], "open_questions": []}

            # Try parsing JSON directly
            result = json.loads(content)
            if isinstance(result, dict):
                return {
                    "facts": result.get("facts", []),
                    "decisions": result.get("decisions", []),
                    "open_questions": result.get("open_questions", []),
                }

            # Try extracting from markdown code blocks
            result = extract_json_from_text(content)
            if result:
                return {
                    "facts": result.get("facts", []),
                    "decisions": result.get("decisions", []),
                    "open_questions": result.get("open_questions", []),
                }

            # Last resort: retry with repair prompt
            logger.warning(
                "JSON parse failed, attempting repair",
                extra={"event": "extractor.pass1.json_repair"},
            )
            repair_content = self.fast_llm.chat(
                model=self.fast_model,
                system="You are a JSON repair assistant. Extract and return ONLY valid JSON, no other text.",
                user=f"Repair this JSON output to be valid:\n\n{content}",
                temperature=0.1,
            )
            if repair_content:
                result = extract_json_from_text(repair_content) or json.loads(repair_content)
                if result:
                    return {
                        "facts": result.get("facts", []),
                        "decisions": result.get("decisions", []),
                        "open_questions": result.get("open_questions", []),
                    }

            logger.error(
                "Failed to parse JSON after repair",
                extra={
                    "event": "extractor.pass1.json_parse_failed",
                    "response_preview": content[:200] if content else None,
                },
            )
            return {"facts": [], "decisions": [], "open_questions": []}

        except Exception as e:
            logger.exception(
                "Error in fast extraction",
                extra={"event": "extractor.pass1.error"},
            )
            return {"facts": [], "decisions": [], "open_questions": []}

    def refine_atoms(
        self,
        all_candidates: dict[str, list[dict[str, Any]]],
        conversation_id: str,
        conversation_title: str | None,
    ) -> dict[str, Any]:
        """
        Refine and consolidate candidate atoms (Pass 2).

        Args:
            all_candidates: Dict with "facts", "decisions", "open_questions" lists
            conversation_id: Conversation identifier
            conversation_title: Optional conversation title

        Returns:
            Dict with refined/deduplicated atoms
        """
        # Pre-deduplicate candidates locally to reduce payload size
        deduplicated = deduplicate_candidates(all_candidates)

        # Prepare candidates JSON for prompt (compact format to reduce tokens)
        candidates_json = json.dumps(
            deduplicated, ensure_ascii=False, separators=(",", ":")
        )

        prompt = PASS2_REFINEMENT_PROMPT.format(
            conversation_id=conversation_id,
            conversation_title=conversation_title or "Unknown",
            all_candidates_json=candidates_json,
        )

        try:
            content = self.big_llm.chat(
                model=self.big_model,
                system="You are a knowledge refinement assistant. Return only valid JSON matching the schema, no markdown, no code blocks.",
                user=prompt,
                temperature=0.2,
                json_object=True,
            )

            if not content:
                logger.warning(
                    "Empty response from refinement, using candidates as-is",
                    extra={
                        "event": "extractor.pass2.empty_response",
                        "conversation_id": conversation_id,
                    },
                )
                return all_candidates

            result = json.loads(content)
            if not isinstance(result, dict):
                logger.warning(
                    "Invalid response format, using candidates as-is",
                    extra={
                        "event": "extractor.pass2.invalid_format",
                        "conversation_id": conversation_id,
                    },
                )
                return all_candidates

            # Ensure all keys are present
            return {
                "facts": result.get("facts", []),
                "decisions": result.get("decisions", []),
                "open_questions": result.get("open_questions", []),
            }

        except Exception as e:
            logger.exception(
                "Error in refinement, falling back to candidates",
                extra={
                    "event": "extractor.pass2.error",
                    "conversation_id": conversation_id,
                },
            )
            return all_candidates
