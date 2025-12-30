"""Hybrid atom extractor that uses OpenRouter for Pass 1 and DSPy for Pass 2."""

from typing import Any

from ck_exporter.adapters.dspy_atom_refiner import DspyAtomRefiner
from ck_exporter.adapters.openrouter_atom_extractor import OpenRouterAtomExtractor
from ck_exporter.core.ports.atom_extractor import AtomExtractor


class HybridAtomExtractor:
    """
    Hybrid atom extractor that combines OpenRouter (Pass 1) and DSPy (Pass 2).

    This allows using DSPy for refinement while keeping the proven OpenRouter
    extraction logic for chunk processing.
    """

    def __init__(
        self,
        openrouter_extractor: OpenRouterAtomExtractor,
        dspy_refiner: DspyAtomRefiner,
    ):
        """
        Initialize hybrid extractor.

        Args:
            openrouter_extractor: OpenRouter extractor for Pass 1
            dspy_refiner: DSPy refiner for Pass 2
        """
        self.openrouter_extractor = openrouter_extractor
        self.dspy_refiner = dspy_refiner

    def extract_from_chunk(self, chunk_text: str) -> dict[str, Any]:
        """
        Extract candidate atoms from a conversation chunk (Pass 1).

        Delegates to OpenRouter extractor.

        Args:
            chunk_text: Formatted conversation chunk text

        Returns:
            Dict with keys: "facts", "decisions", "open_questions"
        """
        return self.openrouter_extractor.extract_from_chunk(chunk_text)

    def refine_atoms(
        self,
        all_candidates: dict[str, list[dict[str, Any]]],
        conversation_id: str,
        conversation_title: str | None,
    ) -> dict[str, Any]:
        """
        Refine and consolidate candidate atoms (Pass 2).

        Delegates to DSPy refiner.

        Args:
            all_candidates: Dict with "facts", "decisions", "open_questions" lists
            conversation_id: Conversation identifier
            conversation_title: Optional conversation title

        Returns:
            Dict with refined/deduplicated atoms
        """
        return self.dspy_refiner.refine_atoms(all_candidates, conversation_id, conversation_title)
