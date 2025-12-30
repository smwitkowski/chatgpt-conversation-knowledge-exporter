"""Linearize command."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ck_exporter.pipeline.linearize import linearize_export

console = Console()


def linearize_command(
    input: Path = typer.Option(
        ...,
        "--input",
        "-i",
        help="Path to ChatGPT export JSON (list), single-conversation JSON (mapping/current_node), Claude export JSON, or a directory of per-conversation .json files",
    ),
    out: Path = typer.Option(Path("_evidence"), "--out", "-o", help="Output directory for evidence"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Limit number of conversations to process (deterministic: first N by sorted filename)"),
) -> None:
    """Linearize conversations from export JSON into markdown."""
    if not input.exists():
        console.print(f"[red]Input path not found: {input}[/red]")
        raise typer.Exit(1)

    linearize_export(input, out, limit=limit)
