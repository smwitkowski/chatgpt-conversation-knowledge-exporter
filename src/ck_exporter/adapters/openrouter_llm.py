"""OpenRouter-backed LLM client adapter."""

import os
import threading
from typing import Optional

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from ck_exporter.adapters.openrouter_client import make_openrouter_client
from ck_exporter.core.ports.llm import LLMClient

# Global in-flight request semaphore (process-wide)
_inflight_semaphore: Optional[threading.BoundedSemaphore] = None
_inflight_lock = threading.Lock()


def _get_inflight_semaphore() -> threading.BoundedSemaphore:
    """Get or create the global in-flight request semaphore."""
    global _inflight_semaphore
    if _inflight_semaphore is None:
        with _inflight_lock:
            if _inflight_semaphore is None:
                # Default: derive from CKX_MAX_CONCURRENCY or use conservative default
                max_concurrency = int(os.getenv("CKX_MAX_CONCURRENCY", "8"))
                max_inflight = int(os.getenv("CKX_LLM_MAX_INFLIGHT", str(max_concurrency * 4)))
                _inflight_semaphore = threading.BoundedSemaphore(max_inflight)
    return _inflight_semaphore


class OpenRouterLLMClient:
    """OpenRouter-backed implementation of LLMClient."""

    def __init__(self, use_openrouter: bool = True, client: Optional[OpenAI] = None):
        """
        Initialize OpenRouter LLM client.

        Args:
            use_openrouter: If True, use OpenRouter API; otherwise use standard OpenAI
            client: Optional pre-configured OpenAI client (for testing/sharing)
        """
        self._client = client if client is not None else make_openrouter_client(use_openrouter)
        self._semaphore = _get_inflight_semaphore()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
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
            Generated text content
        """
        kwargs = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
        }
        if json_object:
            kwargs["response_format"] = {"type": "json_object"}

        # Acquire semaphore to limit in-flight requests
        self._semaphore.acquire()
        try:
            response = self._client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            return content if content else ""
        finally:
            self._semaphore.release()
