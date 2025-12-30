"""DSPy language model configuration for OpenRouter."""

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def configure_dspy_lm(model: str, use_openrouter: bool = True):
    """
    Configure DSPy language model for OpenRouter.

    Args:
        model: Model identifier (e.g., "z-ai/glm-4.7")
        use_openrouter: If True, use OpenRouter API; otherwise use standard OpenAI

    Returns:
        Configured DSPy LM instance

    Raises:
        ImportError: If dspy-ai is not installed
        ValueError: If API key is missing
    """
    try:
        import dspy
    except ImportError:
        raise ImportError(
            "dspy-ai is not installed. Install it with: uv sync --extra dspy"
        ) from None

    if use_openrouter:
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY or OPENAI_API_KEY must be set in environment")

        # Configure OpenRouter base URL
        base_url = "https://openrouter.ai/api/v1"

        # Optional attribution headers
        extra_headers = {}
        http_referer = os.getenv("OPENROUTER_HTTP_REFERER")
        x_title = os.getenv("OPENROUTER_X_TITLE", "ChatGPT Conversation Knowledge Exporter")
        if http_referer:
            extra_headers["HTTP-Referer"] = http_referer
        if x_title:
            extra_headers["X-Title"] = x_title

        # DSPy/LiteLLM requires "openrouter/" prefix for OpenRouter models
        if not model.startswith("openrouter/"):
            dspy_model = f"openrouter/{model}"
        else:
            dspy_model = model

        # Create DSPy LM with OpenRouter
        lm = dspy.LM(
            model=dspy_model,
            api_key=api_key,
            api_base=base_url,
            extra_headers=extra_headers if extra_headers else None,
        )
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment")

        lm = dspy.LM(model=model, api_key=api_key)

    return lm


def get_dspy_lm_for_labeling(use_openrouter: bool = True) -> "dspy.LM":
    """
    Get DSPy LM configured for topic labeling.

    Args:
        use_openrouter: Whether to use OpenRouter

    Returns:
        Configured DSPy LM instance
    """
    model = os.getenv("CKX_DSPY_LABEL_MODEL", "z-ai/glm-4.7")
    return configure_dspy_lm(model, use_openrouter=use_openrouter)


def get_dspy_lm_for_refinement(use_openrouter: bool = True) -> "dspy.LM":
    """
    Get DSPy LM configured for atom refinement.

    Args:
        use_openrouter: Whether to use OpenRouter

    Returns:
        Configured DSPy LM instance
    """
    model = os.getenv("CKX_DSPY_REFINE_MODEL", "z-ai/glm-4.7")
    return configure_dspy_lm(model, use_openrouter=use_openrouter)
