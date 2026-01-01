"""OpenRouter-backed topic labeler adapter."""

import json
from typing import Any

from ck_exporter.config import get_llm_max_tokens
from ck_exporter.core.ports.llm import LLMClient
from ck_exporter.core.ports.topic_labeler import TopicLabeler
from ck_exporter.logging import get_logger
from ck_exporter.programs.json_extract import extract_json_from_text

logger = get_logger(__name__)


class OpenRouterTopicLabeler:
    """OpenRouter-backed implementation of TopicLabeler."""

    def __init__(
        self,
        llm: LLMClient,
        model: str = "z-ai/glm-4.7",
    ):
        """
        Initialize topic labeler.

        Args:
            llm: LLM client for labeling
            model: Model identifier for labeling
        """
        self.llm = llm
        self.model = model

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
        # Build prompt for LLM labeling
        doc_samples = "\n\n---\n\n".join(
            [f"Conversation ID: {conv_id}\n\n{doc_text[:500]}..." for conv_id, doc_text in representative_docs]
        )

        prompt = f"""You are analyzing a topic cluster discovered from conversation data.

Here are 3 representative conversations from this topic cluster:

{doc_samples}

Based on these conversations, generate:
1. A short topic name (3-5 words) that captures the main theme
2. A 1-2 sentence description of what this topic is about

Return ONLY valid JSON with this structure:
{{
  "name": "Topic Name Here",
  "description": "Description here."
}}"""

        try:
            content = self.llm.chat(
                model=self.model,
                system="You are a topic labeling assistant. Return only valid JSON.",
                user=prompt,
                temperature=0.3,
                max_tokens=get_llm_max_tokens("TOPIC_LABEL"),
            )

            if content:
                # Try to extract JSON
                if "```json" in content:
                    start = content.find("```json") + 7
                    end = content.find("```", start)
                    if end > start:
                        content = content[start:end].strip()
                elif "```" in content:
                    start = content.find("```") + 3
                    end = content.find("```", start)
                    if end > start:
                        content = content[start:end].strip()

                label_data = extract_json_from_text(content) or json.loads(content)
                name = label_data.get("name", f"Topic {topic_id}")
                description = label_data.get("description", "No description available")
            else:
                name = f"Topic {topic_id}"
                description = "No description available"
        except Exception as e:
            logger.warning(
                "Failed to label topic",
                extra={
                    "event": "labeler.topic.error",
                    "topic_id": topic_id,
                },
                exc_info=True,
            )
            name = f"Topic {topic_id}"
            description = "No description available"

        return {"name": name, "description": description}
