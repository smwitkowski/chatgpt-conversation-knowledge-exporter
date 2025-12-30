"""Topic labeler port interface."""

from typing import Any, Protocol


class TopicLabeler(Protocol):
    """Interface for labeling discovered topic clusters."""

    def label_topic(
        self,
        topic_id: int,
        representative_docs: list[tuple[str, str]],
        keywords: list[str],
    ) -> dict[str, str]:
        """
        Generate a label (name + description) for a topic cluster.

        Args:
            topic_id: Numeric topic identifier
            representative_docs: List of (conversation_id, doc_text) tuples
            keywords: Top keywords from topic model

        Returns:
            Dict with "name" and "description" keys
        """
        ...
