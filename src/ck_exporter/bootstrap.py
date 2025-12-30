"""Composition root for building adapters and wiring dependencies.

This module centralizes all adapter selection logic based on environment variables,
ensuring a single source of truth for dependency injection.
"""

import os
from typing import Optional

from ck_exporter.adapters.dspy_atom_refiner import DspyAtomRefiner
from ck_exporter.adapters.dspy_topic_labeler import DspyTopicLabeler
from ck_exporter.adapters.hybrid_atom_extractor import HybridAtomExtractor
from ck_exporter.adapters.openrouter_atom_extractor import OpenRouterAtomExtractor
from ck_exporter.adapters.openrouter_client import make_openrouter_client
from ck_exporter.adapters.openrouter_embedder import OpenRouterEmbedder
from ck_exporter.adapters.openrouter_llm import OpenRouterLLMClient
from ck_exporter.adapters.openrouter_topic_labeler import OpenRouterTopicLabeler
from ck_exporter.core.ports.atom_extractor import AtomExtractor
from ck_exporter.core.ports.embedder import Embedder
from ck_exporter.core.ports.llm import LLMClient
from ck_exporter.core.ports.topic_labeler import TopicLabeler
from ck_exporter.logging import get_logger

logger = get_logger(__name__)


def build_llm_client(use_openrouter: bool = True, client: Optional[object] = None) -> LLMClient:
    """
    Build an LLM client adapter.

    Args:
        use_openrouter: Whether to use OpenRouter (default True)
        client: Optional pre-configured OpenAI client (for sharing)

    Returns:
        Configured LLMClient instance
    """
    if client is None:
        client = make_openrouter_client(use_openrouter)
    return OpenRouterLLMClient(use_openrouter=use_openrouter, client=client)


def build_embedder(
    model: str = "openai/text-embedding-3-small",
    use_openrouter: bool = True,
    client: Optional[object] = None,
) -> Embedder:
    """
    Build an embedder adapter.

    Args:
        model: Embedding model identifier
        use_openrouter: Whether to use OpenRouter (default True)
        client: Optional pre-configured OpenAI client (for sharing)

    Returns:
        Configured Embedder instance
    """
    if client is None:
        client = make_openrouter_client(use_openrouter)
    return OpenRouterEmbedder(model=model, use_openrouter=use_openrouter, client=client)


def build_atom_extractor(
    fast_model: Optional[str] = None,
    big_model: Optional[str] = None,
    use_openrouter: bool = True,
    shared_client: Optional[object] = None,
) -> AtomExtractor:
    """
    Build an atom extractor adapter based on environment configuration.

    Reads `CKX_ATOM_REFINER_IMPL` to choose between:
    - `openrouter`: OpenRouter for both Pass 1 and Pass 2 (default)
    - `dspy`: OpenRouter for Pass 1, DSPy for Pass 2 (hybrid)

    Args:
        fast_model: Model for Pass 1 (defaults to env or "z-ai/glm-4.7")
        big_model: Model for Pass 2 (defaults to env or "z-ai/glm-4.7")
        use_openrouter: Whether to use OpenRouter (default True)
        shared_client: Optional pre-configured OpenAI client (for efficiency)

    Returns:
        Configured AtomExtractor instance
    """
    # Set defaults from environment or hardcoded defaults
    fast_model = fast_model or os.getenv("CKX_FAST_MODEL", "z-ai/glm-4.7")
    big_model = big_model or os.getenv("CKX_BIG_MODEL", "z-ai/glm-4.7")

    # Create shared client if not provided
    if shared_client is None:
        shared_client = make_openrouter_client(use_openrouter)

    # Create LLM clients
    fast_llm = build_llm_client(use_openrouter=use_openrouter, client=shared_client)
    big_llm = build_llm_client(use_openrouter=use_openrouter, client=shared_client)

    # Check if DSPy refinement is requested
    refiner_impl = os.getenv("CKX_ATOM_REFINER_IMPL", "openrouter").lower()

    if refiner_impl == "dspy":
        try:
            # Create OpenRouter extractor for Pass 1
            openrouter_extractor = OpenRouterAtomExtractor(
                fast_llm=fast_llm,
                big_llm=big_llm,  # Not used in hybrid mode, but required for constructor
                fast_model=fast_model,
                big_model=big_model,
            )

            # Create DSPy refiner for Pass 2
            dspy_refiner = DspyAtomRefiner(use_openrouter=use_openrouter)

            # Wrap in hybrid extractor
            return HybridAtomExtractor(
                openrouter_extractor=openrouter_extractor,
                dspy_refiner=dspy_refiner,
            )
        except ImportError as e:
            logger.warning(
                "DSPy atom refiner requested but not available, falling back to OpenRouter",
                extra={
                    "event": "bootstrap.dspy_refiner.unavailable",
                    "error": str(e),
                },
            )
            # Fall through to default OpenRouter implementation

    # Default: OpenRouter for both passes
    return OpenRouterAtomExtractor(
        fast_llm=fast_llm,
        big_llm=big_llm,
        fast_model=fast_model,
        big_model=big_model,
    )


def build_topic_labeler(
    label_model: Optional[str] = None,
    use_openrouter: bool = True,
    shared_client: Optional[object] = None,
) -> TopicLabeler:
    """
    Build a topic labeler adapter based on environment configuration.

    Reads `CKX_TOPIC_LABELER_IMPL` to choose between:
    - `openrouter`: OpenRouter-based labeler (default)
    - `dspy`: DSPy-based labeler

    Args:
        label_model: Model for labeling (defaults to env or "z-ai/glm-4.7")
        use_openrouter: Whether to use OpenRouter (default True)
        shared_client: Optional pre-configured OpenAI client (for efficiency)

    Returns:
        Configured TopicLabeler instance
    """
    if label_model is None:
        label_model = os.getenv("CKX_DSPY_LABEL_MODEL", "z-ai/glm-4.7")

    # Choose labeler implementation based on env flag
    labeler_impl = os.getenv("CKX_TOPIC_LABELER_IMPL", "openrouter").lower()

    if labeler_impl == "dspy":
        try:
            return DspyTopicLabeler(use_openrouter=use_openrouter)
        except ImportError as e:
            logger.warning(
                "DSPy topic labeler requested but not available, falling back to OpenRouter",
                extra={
                    "event": "bootstrap.dspy_labeler.unavailable",
                    "error": str(e),
                },
            )
            # Fall through to default OpenRouter implementation

    # Default: OpenRouter
    if shared_client is None:
        shared_client = make_openrouter_client(use_openrouter)
    llm = build_llm_client(use_openrouter=use_openrouter, client=shared_client)
    return OpenRouterTopicLabeler(llm=llm, model=label_model)
