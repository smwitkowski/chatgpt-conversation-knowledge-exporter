"""DSPy-backed atom refiner adapter."""

import json
from typing import Any

from ck_exporter.adapters.dspy_lm import get_dspy_lm_for_refinement
from ck_exporter.logging import get_logger
from ck_exporter.programs.dspy.refine_atoms import create_refine_atoms_program

logger = get_logger(__name__)


class DspyAtomRefiner:
    """DSPy-backed implementation of atom refinement logic."""

    def __init__(self, use_openrouter: bool = True, lm: Any = None):
        """
        Initialize DSPy atom refiner.

        Args:
            use_openrouter: Whether to use OpenRouter
            lm: Optional pre-configured DSPy LM (for testing)
        """
        try:
            import dspy
        except ImportError:
            raise ImportError(
                "dspy-ai is not installed. Install it with: uv sync --extra dspy"
            ) from None

        if lm is None:
            lm = get_dspy_lm_for_refinement(use_openrouter=use_openrouter)

        self.program = create_refine_atoms_program(lm)

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
        # Prepare candidates JSON
        candidates_json = json.dumps(all_candidates, ensure_ascii=False, indent=2)

        try:
            # Call DSPy program
            result = self.program(
                conversation_id=conversation_id,
                conversation_title=conversation_title or "Unknown",
                candidates_json=candidates_json,
            )

            # Parse JSON outputs
            facts_json = result.get("facts_json", "[]")
            decisions_json = result.get("decisions_json", "[]")
            open_questions_json = result.get("open_questions_json", "[]")

            # Validate and parse
            try:
                facts = json.loads(facts_json)
                decisions = json.loads(decisions_json)
                open_questions = json.loads(open_questions_json)

                # Ensure they are lists
                if not isinstance(facts, list):
                    logger.warning(
                        "DSPy returned non-list facts, using candidates as-is",
                        extra={
                            "event": "refiner.dspy.invalid_type",
                            "conversation_id": conversation_id,
                            "type": "facts",
                        },
                    )
                    return all_candidates
                if not isinstance(decisions, list):
                    logger.warning(
                        "DSPy returned non-list decisions, using candidates as-is",
                        extra={
                            "event": "refiner.dspy.invalid_type",
                            "conversation_id": conversation_id,
                            "type": "decisions",
                        },
                    )
                    return all_candidates
                if not isinstance(open_questions, list):
                    logger.warning(
                        "DSPy returned non-list questions, using candidates as-is",
                        extra={
                            "event": "refiner.dspy.invalid_type",
                            "conversation_id": conversation_id,
                            "type": "questions",
                        },
                    )
                    return all_candidates

                return {
                    "facts": facts,
                    "decisions": decisions,
                    "open_questions": open_questions,
                }

            except json.JSONDecodeError as e:
                logger.warning(
                    "Failed to parse DSPy JSON output, using candidates as-is",
                    extra={
                        "event": "refiner.dspy.json_parse_error",
                        "conversation_id": conversation_id,
                    },
                    exc_info=True,
                )
                return all_candidates

        except Exception as e:
            logger.exception(
                "Error in DSPy refinement, falling back to candidates",
                extra={
                    "event": "refiner.dspy.error",
                    "conversation_id": conversation_id,
                },
            )
            return all_candidates
