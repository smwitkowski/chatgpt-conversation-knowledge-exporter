"""LLM client port interface."""

from typing import Protocol


class LLMClient(Protocol):
    """Interface for LLM chat/completion services."""

    def chat(
        self,
        model: str,
        system: str,
        user: str,
        *,
        temperature: float = 0.3,
        json_object: bool = False,
    ) -> str:
        """
        Generate a chat completion.

        Args:
            model: Model identifier (e.g., "z-ai/glm-4.7")
            system: System message content
            user: User message content
            temperature: Sampling temperature (default 0.3)
            json_object: If True, request JSON object response format

        Returns:
            Generated text content (may contain JSON if json_object=True)
        """
        ...
