"""LangSmith tracing utilities for the ChatGPT Conversation Knowledge Exporter.

This module provides utilities to enable LangSmith tracing for both OpenAI/OpenRouter
LLM calls and DSPy program executions. Tracing is controlled via environment variables
and gracefully degrades when LangSmith is not available.

Environment Variables:
- LANGSMITH_TRACING: Set to "true" to enable tracing
- LANGSMITH_API_KEY: Required API key for LangSmith
- LANGSMITH_PROJECT: Optional project name (defaults to "chatgpt-conversation-knowledge-exporter")
- LANGSMITH_WORKSPACE_ID: Optional workspace ID for org-scoped keys
- LANGSMITH_ENDPOINT: Optional endpoint (defaults to https://api.smith.langchain.com)

When enabled, full prompts and outputs are sent to LangSmith for debugging and monitoring.
"""

import contextlib
import contextvars
import os
from typing import Any, Dict

from ck_exporter.logging import get_logger

logger = get_logger(__name__)

# Context-local storage for tracing metadata (works with LangSmith contextvars and can be
# propagated into new threads using contextvars.copy_context()).
_TRACE_METADATA: contextvars.ContextVar[dict[str, Any]] = contextvars.ContextVar(
    "ckx_langsmith_trace_metadata", default={}
)


def is_langsmith_enabled() -> bool:
    """Check if LangSmith tracing should be enabled."""
    return os.getenv("LANGSMITH_TRACING", "").lower() in ("true", "1", "yes")


def ensure_default_project_name() -> None:
    """Ensure LANGSMITH_PROJECT is set to a default if not already configured."""
    if not os.getenv("LANGSMITH_PROJECT"):
        os.environ["LANGSMITH_PROJECT"] = "chatgpt-conversation-knowledge-exporter"
        logger.info(
            "Set default LangSmith project name",
            extra={
                "event": "observability.langsmith.default_project",
                "project_name": "chatgpt-conversation-knowledge-exporter",
            },
        )


def maybe_wrap_openai_client(client: Any) -> Any:
    """
    Wrap an OpenAI client with LangSmith tracing if enabled.

    Args:
        client: The openai.OpenAI client instance to potentially wrap

    Returns:
        Wrapped client if LangSmith is enabled and available, otherwise the original client
    """
    if not is_langsmith_enabled():
        return client

    try:
        from langsmith.wrappers import wrap_openai

        ensure_default_project_name()
        wrapped_client = wrap_openai(client)
        logger.info(
            "Wrapped OpenAI client with LangSmith tracing",
            extra={"event": "observability.langsmith.client_wrapped"},
        )
        return wrapped_client

    except ImportError:
        logger.warning(
            "LangSmith tracing enabled but langsmith package not installed. "
            "Install with: uv sync --extra observability",
            extra={"event": "observability.langsmith.missing_package"},
        )
        return client

    except Exception as e:
        logger.warning(
            "Failed to wrap OpenAI client with LangSmith",
            extra={
                "event": "observability.langsmith.wrap_error",
                "error": str(e),
            },
        )
        return client


def get_dspy_callbacks() -> list[Any]:
    """
    Get DSPy callbacks for LangSmith tracing if enabled.

    Returns:
        List of DSPy callbacks (empty if tracing disabled or langsmith not available)
    """
    if not is_langsmith_enabled():
        return []

    try:
        # First check if langsmith is available
        import langsmith
        from ck_exporter.observability.dspy_langsmith_callback import LangSmithDSPyCallback

        ensure_default_project_name()
        callback = LangSmithDSPyCallback()
        logger.info(
            "Initialized DSPy LangSmith callback",
            extra={"event": "observability.langsmith.dspy_callback_init"},
        )
        return [callback]

    except ImportError:
        logger.warning(
            "LangSmith tracing enabled but langsmith package not installed. "
            "Install with: uv sync --extra observability",
            extra={"event": "observability.langsmith.missing_package"},
        )
        return []

    except Exception as e:
        logger.warning(
            "Failed to initialize DSPy LangSmith callback",
            extra={
                "event": "observability.langsmith.dspy_callback_error",
                "error": str(e),
            },
        )
        return []


def configure_dspy_with_langsmith(lm: Any) -> None:
    """
    Configure DSPy with LangSmith callbacks if tracing is enabled.

    This is a drop-in replacement for dspy.configure(lm=lm) that also
    enables tracing when available.

    Args:
        lm: DSPy language model to configure
    """
    import dspy

    callbacks = get_dspy_callbacks()
    dspy.configure(lm=lm, callbacks=callbacks)


def get_tracing_metadata() -> Dict[str, Any]:
    """
    Get current tracing metadata from thread-local storage.

    Returns:
        Dictionary with metadata keys like conversation_id, step, topic_id, etc.
    """
    return dict(_TRACE_METADATA.get() or {})


def set_tracing_metadata(**metadata: Any) -> None:
    """
    Set tracing metadata in thread-local storage.

    Args:
        **metadata: Key-value pairs for metadata (e.g., conversation_id, step, topic_id)
    """
    _TRACE_METADATA.set(dict(metadata))


def clear_tracing_metadata() -> None:
    """Clear tracing metadata from thread-local storage."""
    _TRACE_METADATA.set({})


@contextlib.contextmanager
def tracing_context(**metadata: Any):
    """
    Context manager for setting tracing metadata.

    Usage:
        with tracing_context(conversation_id="abc-123", step="extract"):
            # LLM calls here will include the metadata
            llm.chat(...)

    Args:
        **metadata: Key-value pairs for metadata (e.g., conversation_id, step, topic_id)
    """
    prev_metadata = get_tracing_metadata()
    merged_metadata = {**prev_metadata, **metadata}
    token = _TRACE_METADATA.set(merged_metadata)
    try:
        yield
    finally:
        _TRACE_METADATA.reset(token)


def traceable_call(
    fn,
    *,
    name: str,
    run_type: str = "chain",
    metadata: dict[str, Any] | None = None,
    tags: list[str] | None = None,
):
    """
    Execute a callable within a LangSmith parent run (if enabled and available).

    This is used to create a parent run so that wrapped OpenAI calls show up
    as children in the waterfall trace.
    """
    if not is_langsmith_enabled():
        return fn()
    try:
        from langsmith import traceable  # type: ignore

        ensure_default_project_name()
        traced = traceable(fn, name=name, run_type=run_type)
        extra: dict[str, Any] = {}
        if metadata:
            extra["metadata"] = metadata
        if tags:
            extra["tags"] = tags
        # traceable-wrapped call accepts langsmith_extra
        return traced(langsmith_extra=extra) if extra else traced()
    except ImportError:
        return fn()
