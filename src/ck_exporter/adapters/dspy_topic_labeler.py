"""DSPy-backed topic labeler adapter."""

import json
from typing import Any

from ck_exporter.adapters.dspy_lm import get_dspy_lm_for_labeling
from ck_exporter.core.ports.topic_labeler import TopicLabeler
from ck_exporter.logging import get_logger
from ck_exporter.programs.dspy.label_topic import create_label_topic_program

logger = get_logger(__name__)


class DspyTopicLabeler:
    """DSPy-backed implementation of TopicLabeler."""

    def __init__(self, use_openrouter: bool = True, lm: Any = None):
        """
        Initialize DSPy topic labeler.

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
            lm = get_dspy_lm_for_labeling(use_openrouter=use_openrouter)

        self.program = create_label_topic_program(lm)

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
        # Format representative docs
        doc_samples = "\n\n---\n\n".join(
            [f"Conversation ID: {conv_id}\n\n{doc_text[:500]}..." for conv_id, doc_text in representative_docs]
        )

        # Format keywords
        keywords_str = ", ".join(keywords[:10])

        try:
            # Call DSPy program
            result = self.program(representative_docs=doc_samples, keywords=keywords_str)

            # Validate result
            name = result.get("name", "").strip()
            description = result.get("description", "").strip()

            if not name:
                logger.warning(
                    "Empty name from DSPy, using fallback",
                    extra={
                        "event": "labeler.dspy.empty_name",
                        "topic_id": topic_id,
                    },
                )
                name = f"Topic {topic_id}"

            if not description:
                logger.warning(
                    "Empty description from DSPy, using fallback",
                    extra={
                        "event": "labeler.dspy.empty_description",
                        "topic_id": topic_id,
                    },
                )
                description = "No description available"

            return {"name": name, "description": description}

        except Exception as e:
            logger.warning(
                "Failed to label topic with DSPy",
                extra={
                    "event": "labeler.dspy.error",
                    "topic_id": topic_id,
                },
                exc_info=True,
            )
            return {"name": f"Topic {topic_id}", "description": "No description available"}
