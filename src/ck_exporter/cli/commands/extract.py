"""Extract command."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ck_exporter.extract_openai import extract_export

console = Console()


def extract_command(
    input: Path = typer.Option(
        ...,
        "--input",
        "-i",
        help="Path to ChatGPT export JSON (list), single-conversation JSON (mapping/current_node), Claude export JSON, or a directory of per-conversation .json files",
    ),
    evidence: Path = typer.Option(Path("_evidence"), "--evidence", "-e", help="Evidence directory"),
    out: Path = typer.Option(Path("_atoms"), "--out", "-o", help="Output directory for atoms"),
    fast_model: str = typer.Option(None, "--fast-model", help="Fast model for Pass 1 (default: z-ai/glm-4.7)"),
    big_model: str = typer.Option(None, "--big-model", help="Big model for Pass 2 (default: z-ai/glm-4.7)"),
    max_concurrency: int = typer.Option(None, "--max-concurrency", help="Max concurrent conversations (default: 8)"),
    skip_existing: bool = typer.Option(True, "--skip-existing/--no-skip-existing", help="Skip conversations with existing outputs"),
    use_openrouter: bool = typer.Option(True, "--openrouter/--no-openrouter", help="Use OpenRouter API (default: True)"),
    conversation_id: str = typer.Option(None, "--conversation-id", "-c", help="Process only this conversation ID (for testing)"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Limit number of conversations to process (deterministic: first N by sorted filename)"),
) -> None:
    """Extract knowledge atoms from conversations using two-pass OpenRouter pipeline."""
    if not input.exists():
        console.print(f"[red]Input path not found: {input}[/red]")
        raise typer.Exit(1)

    extract_export(
        input,
        evidence,
        out,
        fast_model=fast_model,
        big_model=big_model,
        max_concurrency=max_concurrency,
        skip_existing=skip_existing,
        use_openrouter=use_openrouter,
        conversation_id=conversation_id,
        limit=limit,
    )
