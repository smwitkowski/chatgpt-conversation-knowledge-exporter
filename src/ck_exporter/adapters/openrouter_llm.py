"""OpenRouter-backed LLM client adapter."""

import threading
from typing import Optional

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from ck_exporter.adapters.openrouter_client import make_openrouter_client
from ck_exporter.config import get_llm_max_inflight
from ck_exporter.core.ports.llm import LLMClient
from ck_exporter.observability.langsmith import get_tracing_metadata, is_langsmith_enabled

# Global in-flight request semaphore (process-wide)
_inflight_semaphore: Optional[threading.BoundedSemaphore] = None
_inflight_lock = threading.Lock()


def _get_inflight_semaphore() -> threading.BoundedSemaphore:
    """Get or create the global in-flight request semaphore."""
    global _inflight_semaphore
    if _inflight_semaphore is None:
        with _inflight_lock:
            if _inflight_semaphore is None:
                # Get max in-flight from config (defaults to max_concurrency * 4)
                max_inflight = get_llm_max_inflight()
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
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate a chat completion.

        Args:
            model: Model identifier (e.g., "z-ai/glm-4.7")
            system: System message content
            user: User message content
            temperature: Sampling temperature (default 0.3)
            json_object: If True, request JSON object response format
            max_tokens: Optional maximum tokens to generate (default None = no cap)

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
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        # Add LangSmith metadata if available and enabled
        # Only add langsmith_extra when LangSmith is actually enabled AND available, as unwrapped
        # OpenAI clients don't accept this parameter
        if is_langsmith_enabled():
            # Check if langsmith is actually available (importable)
            try:
                import langsmith  # type: ignore
                langsmith_available = True
            except ImportError:
                langsmith_available = False

            if langsmith_available:
                metadata = get_tracing_metadata()
                if metadata:
                    # LangSmith wrapped clients expect langsmith_extra to include structured keys
                    # like {"metadata": {...}, "tags": [...], "run_name": "..."}.
                    step = metadata.get("step")
                    run_name = None
                    if step:
                        run_name = f"{step}"
                        if "conversation_id" in metadata:
                            run_name += f" ({metadata['conversation_id']})"
                    extra: dict[str, object] = {"metadata": metadata}
                    if step:
                        extra["tags"] = [str(step)]
                    if run_name:
                        extra["run_name"] = run_name
                    kwargs["langsmith_extra"] = extra

        # Acquire semaphore to limit in-flight requests
        self._semaphore.acquire()
        try:
            response = self._client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            return content if content else ""
        finally:
            self._semaphore.release()
