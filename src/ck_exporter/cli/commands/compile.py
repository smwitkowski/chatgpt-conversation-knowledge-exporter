"""Compile command."""

from pathlib import Path

import typer

from ck_exporter.pipeline.compile import compile_docs


def compile_command(
    atoms: Path = typer.Option(Path("_atoms"), "--atoms", "-a", help="Atoms directory"),
    out: Path = typer.Option(Path("project/docs"), "--out", "-o", help="Output directory for docs"),
) -> None:
    """Compile documentation from knowledge atoms."""
    compile_docs(atoms, out)
