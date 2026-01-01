"""Configuration management with .env file support."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file from project root (or current directory)
# Try to find project root by looking for pyproject.toml or .env file
_env_loaded = False


def _ensure_env_loaded() -> None:
    """Ensure .env file is loaded (idempotent)."""
    global _env_loaded
    if _env_loaded:
        return

    # Try to find project root
    current = Path.cwd()
    for path in [current, current.parent, current.parent.parent]:
        env_file = path / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            _env_loaded = True
            return

    # If no .env found, still call load_dotenv() to load from current directory
    # or any parent directory (standard dotenv behavior)
    load_dotenv()
    _env_loaded = True


def get_max_concurrency(default: int = 8) -> int:
    """Get maximum concurrent conversations from environment or default."""
    _ensure_env_loaded()
    return int(os.getenv("CKX_MAX_CONCURRENCY", str(default)))


def get_chunk_max_concurrency(default: int = 4) -> int:
    """Get maximum concurrent chunks per conversation from environment or default."""
    _ensure_env_loaded()
    return int(os.getenv("CKX_CHUNK_MAX_CONCURRENCY", str(default)))


def get_llm_max_inflight(default_multiplier: int = 4) -> int:
    """Get maximum in-flight LLM requests from environment or default."""
    _ensure_env_loaded()
    max_concurrency = get_max_concurrency()
    return int(os.getenv("CKX_LLM_MAX_INFLIGHT", str(max_concurrency * default_multiplier)))


def get_topic_max_concurrency(default: int = 8) -> int:
    """Get maximum concurrent topic operations from environment or default."""
    _ensure_env_loaded()
    # Reuse CKX_MAX_CONCURRENCY for topic operations
    return int(os.getenv("CKX_MAX_CONCURRENCY", str(default)))


def _get_optional_int_env(name: str) -> int | None:
    """Get optional integer from environment variable."""
    _ensure_env_loaded()
    v = os.getenv(name)
    if v is None:
        return None
    v = v.strip()
    if not v:
        return None
    try:
        return int(v)
    except ValueError:
        return None


def get_llm_max_tokens(step: str | None = None, default: int | None = None) -> int | None:
    """
    Get per-step max output tokens for OpenRouter/OpenAI chat completions.

    Resolution order:
    1. CKX_LLM_MAX_TOKENS_<STEP> (if step provided)
    2. CKX_LLM_MAX_TOKENS_DEFAULT
    3. default argument
    4. None (no cap)

    Args:
        step: Step identifier (e.g., "TOPIC_LABEL", "EXTRACT_PASS1")
        default: Default value if no env vars are set

    Returns:
        Max tokens (int) or None if no cap should be applied
    """
    if step:
        step_val = _get_optional_int_env(f"CKX_LLM_MAX_TOKENS_{step.upper()}")
        if step_val is not None:
            return step_val

    default_val = _get_optional_int_env("CKX_LLM_MAX_TOKENS_DEFAULT")
    return default_val if default_val is not None else default


def get_dspy_max_tokens(step: str | None = None, default: int | None = None) -> int | None:
    """
    Get per-step max output tokens for DSPy LMs.

    Resolution order:
    1. CKX_DSPY_MAX_TOKENS_<STEP> (if step provided)
    2. CKX_DSPY_MAX_TOKENS_DEFAULT
    3. default argument
    4. None (no cap)

    Args:
        step: Step identifier (e.g., "TOPIC_LABEL", "REFINE_ATOMS")
        default: Default value if no env vars are set

    Returns:
        Max tokens (int) or None if no cap should be applied
    """
    if step:
        step_val = _get_optional_int_env(f"CKX_DSPY_MAX_TOKENS_{step.upper()}")
        if step_val is not None:
            return step_val

    default_val = _get_optional_int_env("CKX_DSPY_MAX_TOKENS_DEFAULT")
    return default_val if default_val is not None else default

