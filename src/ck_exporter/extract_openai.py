"""OpenAI-backed knowledge atom extraction with two-pass OpenRouter pipeline.

This module is a backward-compatible shim that delegates to the new pipeline architecture.
"""

from pathlib import Path
from typing import Callable, Optional

from ck_exporter.adapters.openrouter_client import make_openrouter_client
from ck_exporter.bootstrap import build_atom_extractor
from ck_exporter.config import get_max_concurrency
from ck_exporter.pipeline.extract import extract_export as _extract_export

# Re-export for backward compatibility
__all__ = ["extract_export", "make_openrouter_client"]


def extract_export(
    input_path: Path,
    evidence_dir: Path,
    atoms_dir: Path,
    fast_model: Optional[str] = None,
    big_model: Optional[str] = None,
    max_concurrency: Optional[int] = None,
    skip_existing: bool = True,
    use_openrouter: bool = True,
    conversation_id: Optional[str] = None,
    limit: Optional[int] = None,
    progress_cb: Optional[Callable[[int, int, Optional[dict]], None]] = None,
    non_json_kind: str = "meeting",
) -> None:
    """
    Process export and extract atoms for all conversations using two-pass OpenRouter pipeline.

    This is a backward-compatible wrapper that creates adapters and calls the new pipeline.

    Accepts either:
    - A top-level list of conversations (standard export format)
    - A single conversation object with mapping/current_node
    - A directory containing `.md`/`.docx` files (when non_json_kind="document")

    Args:
        non_json_kind: How to interpret non-JSON files ("meeting" or "document")
    """
    # Set defaults from config or provided value
    max_concurrency = max_concurrency or get_max_concurrency()

    # Create shared client for efficiency
    shared_client = make_openrouter_client(use_openrouter)

    # Build atom extractor using bootstrap (handles env var selection)
    extractor = build_atom_extractor(
        fast_model=fast_model,
        big_model=big_model,
        use_openrouter=use_openrouter,
        shared_client=shared_client,
    )

    # Delegate to pipeline
    _extract_export(
        input_path=input_path,
        evidence_dir=evidence_dir,
        atoms_dir=atoms_dir,
        extractor=extractor,
        max_concurrency=max_concurrency,
        skip_existing=skip_existing,
        conversation_id=conversation_id,
        limit=limit,
        progress_cb=progress_cb,
        non_json_kind=non_json_kind,
    )
