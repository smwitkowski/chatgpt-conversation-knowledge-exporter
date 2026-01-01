"""Consolidate command."""

from pathlib import Path

import typer
from rich.console import Console

from ck_exporter.pipeline.consolidate import consolidate_project

console = Console()


def consolidate_command(
    atoms: Path = typer.Option(Path("_atoms"), "--atoms", "-a", help="Atoms directory (per-conversation)"),
    docs: Path = typer.Option(Path("output/project/docs"), "--docs", "-d", help="Docs directory (per-conversation)"),
    out: Path = typer.Option(Path("output"), "--out", "-o", help="Output directory"),
    include_docs: bool = typer.Option(True, "--include-docs/--no-include-docs", help="Concatenate docs into bundles"),
) -> None:
    """Aggregate per-conversation outputs into a single project-wide knowledge packet (exact dedupe only)."""
    stats = consolidate_project(atoms_dir=atoms, docs_dir=docs, out_dir=out, include_docs=include_docs)
    
    # Build kind summary from atoms_by_kind
    kind_summary = ", ".join([f"{kind}: {count}" for kind, count in sorted(stats.atoms_by_kind.items())])
    
    console.print(
        f"[bold green]✓ Consolidated[/bold green] "
        f"{stats.atoms_in} atoms → {stats.atoms_out} atoms (deduped)"
    )
    if stats.atoms_by_kind:
        console.print(f"   By kind: {kind_summary}")
    console.print(f"   Output: {out / 'project'}")
