"""CLI entrypoint using Typer."""

from pathlib import Path

import typer
from rich.console import Console

from ck_exporter.compile_docs import compile_docs
from ck_exporter.consolidate import consolidate_project
from ck_exporter.extract_openai import extract_export
from ck_exporter.linearize import linearize_export

app = typer.Typer(help="ChatGPT Conversation Knowledge Exporter")
console = Console()


@app.command()
def linearize(
    input: Path = typer.Option(..., "--input", "-i", help="Path to ChatGPT export JSON (list) or single-conversation JSON (object with mapping/current_node)"),
    out: Path = typer.Option(Path("_evidence"), "--out", "-o", help="Output directory for evidence"),
) -> None:
    """Linearize conversations from export JSON into markdown."""
    if not input.exists():
        console.print(f"[red]Input file not found: {input}[/red]")
        raise typer.Exit(1)

    linearize_export(input, out)


@app.command()
def extract(
    input: Path = typer.Option(..., "--input", "-i", help="Path to ChatGPT export JSON (list) or single-conversation JSON (object with mapping/current_node)"),
    evidence: Path = typer.Option(Path("_evidence"), "--evidence", "-e", help="Evidence directory"),
    out: Path = typer.Option(Path("_atoms"), "--out", "-o", help="Output directory for atoms"),
    model: str = typer.Option(None, "--model", "-m", help="OpenAI model to use"),
    conversation_id: str = typer.Option(None, "--conversation-id", "-c", help="Process only this conversation ID (for testing)"),
) -> None:
    """Extract knowledge atoms from conversations using OpenAI."""
    if not input.exists():
        console.print(f"[red]Input file not found: {input}[/red]")
        raise typer.Exit(1)

    extract_export(input, evidence, out, model=model, conversation_id=conversation_id)


@app.command()
def compile(
    atoms: Path = typer.Option(Path("_atoms"), "--atoms", "-a", help="Atoms directory"),
    out: Path = typer.Option(Path("docs"), "--out", "-o", help="Output directory for docs"),
) -> None:
    """Compile documentation from knowledge atoms."""
    compile_docs(atoms, out)


@app.command()
def consolidate(
    atoms: Path = typer.Option(Path("_atoms"), "--atoms", "-a", help="Atoms directory (per-conversation)"),
    docs: Path = typer.Option(Path("docs"), "--docs", "-d", help="Docs directory (per-conversation)"),
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


@app.command()
def run_all(
    input: Path = typer.Option(..., "--input", "-i", help="Path to ChatGPT export JSON (list) or single-conversation JSON (object with mapping/current_node)"),
    evidence_dir: Path = typer.Option(Path("_evidence"), "--evidence", "-e", help="Evidence directory"),
    atoms_dir: Path = typer.Option(Path("_atoms"), "--atoms", "-a", help="Atoms directory"),
    docs_dir: Path = typer.Option(Path("docs"), "--docs", "-d", help="Docs directory"),
    model: str = typer.Option(None, "--model", "-m", help="OpenAI model to use"),
    conversation_id: str = typer.Option(None, "--conversation-id", "-c", help="Process only this conversation ID (for testing)"),
) -> None:
    """Run the full pipeline: linearize → extract → compile."""
    console.print("[bold]Running full pipeline[/bold]")

    # Step 1: Linearize
    console.print("\n[bold cyan]Step 1: Linearizing conversations[/bold cyan]")
    linearize_export(input, evidence_dir)

    # Step 2: Extract
    console.print("\n[bold cyan]Step 2: Extracting knowledge atoms[/bold cyan]")
    extract_export(input, evidence_dir, atoms_dir, model=model, conversation_id=conversation_id)

    # Step 3: Compile
    console.print("\n[bold cyan]Step 3: Compiling documentation[/bold cyan]")
    compile_docs(atoms_dir, docs_dir)

    console.print("\n[bold green]✓ Pipeline complete![/bold green]")


if __name__ == "__main__":
    app()
