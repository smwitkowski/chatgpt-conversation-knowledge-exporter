"""Consolidate command."""

from pathlib import Path

import typer
from rich.console import Console

from ck_exporter.pipeline.consolidate import consolidate_project

console = Console()


def consolidate_command(
    atoms: Path = typer.Option(Path("_atoms"), "--atoms", "-a", help="Atoms directory (per-conversation)"),
    docs: Path = typer.Option(Path("project/docs"), "--docs", "-d", help="Docs directory (per-conversation)"),
    out: Path = typer.Option(Path("output"), "--out", "-o", help="Output directory"),
    include_docs: bool = typer.Option(True, "--include-docs/--no-include-docs", help="Concatenate docs into bundles"),
) -> None:
    """Aggregate per-conversation outputs into a single project-wide knowledge packet (exact dedupe only)."""
    stats = consolidate_project(atoms_dir=atoms, docs_dir=docs, out_dir=out, include_docs=include_docs)
    console.print(
        f"[bold green]✓ Consolidated[/bold green] "
        f"atoms {stats.atoms_in}→{stats.atoms_out}, "
        f"decisions {stats.decisions_in}→{stats.decisions_out}, "
        f"questions {stats.questions_in}→{stats.questions_out} "
        f"into {out / 'project'}"
    )
