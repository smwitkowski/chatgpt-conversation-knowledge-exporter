"""Atom extractor port interface."""

from typing import Any, Protocol


class AtomExtractor(Protocol):
    """Interface for extracting knowledge atoms from conversation chunks."""

    def extract_from_chunk(self, chunk_text: str) -> dict[str, Any]:
        """
        Extract candidate atoms from a conversation chunk (Pass 1).

        Args:
            chunk_text: Formatted conversation chunk text

        Returns:
            Dict with keys: "facts", "decisions", "open_questions"
            Each value is a list of atom dicts
        """
        ...

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
            Dict with keys: "facts", "decisions", "open_questions"
            Each value is a refined/deduplicated list of atom dicts
        """
        ...
