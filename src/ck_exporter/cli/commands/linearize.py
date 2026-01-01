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
    input_kind: str = typer.Option("meeting", "--input-kind", help="How to interpret non-JSON files: meeting|document (default: meeting)"),
) -> None:
    """Linearize conversations from export JSON into markdown."""
    if not input.exists():
        console.print(f"[red]Input path not found: {input}[/red]")
        raise typer.Exit(1)

    if input_kind not in ("meeting", "document"):
        console.print(f"[red]Invalid input-kind: {input_kind}. Must be 'meeting' or 'document'[/red]")
        raise typer.Exit(1)

    if input_kind == "document" and not input.is_dir():
        console.print(f"[red]Document mode requires a directory input, got: {input}[/red]")
        raise typer.Exit(1)

    linearize_export(input, out, limit=limit, non_json_kind=input_kind)
