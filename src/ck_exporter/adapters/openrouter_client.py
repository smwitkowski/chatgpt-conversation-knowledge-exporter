"""Shared OpenRouter/OpenAI client factory."""

import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

from ck_exporter.observability.langsmith import maybe_wrap_openai_client

load_dotenv()


def make_openrouter_client(use_openrouter: bool = True) -> OpenAI:
    """
    Create an OpenAI-compatible client for OpenRouter or standard OpenAI.

    Args:
        use_openrouter: If True, use OpenRouter API; otherwise use standard OpenAI

    Returns:
        Configured OpenAI client
    """
    if use_openrouter:
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY or OPENAI_API_KEY must be set in environment")

        # Optional attribution headers (recommended by OpenRouter)
        extra_headers = {}
        http_referer = os.getenv("OPENROUTER_HTTP_REFERER")
        x_title = os.getenv("OPENROUTER_X_TITLE", "ChatGPT Conversation Knowledge Exporter")
        if http_referer:
            extra_headers["HTTP-Referer"] = http_referer
        if x_title:
            extra_headers["X-Title"] = x_title

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers=extra_headers if extra_headers else None,
        )
        return maybe_wrap_openai_client(client)
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment")
        client = OpenAI(api_key=api_key)
        return maybe_wrap_openai_client(client)
