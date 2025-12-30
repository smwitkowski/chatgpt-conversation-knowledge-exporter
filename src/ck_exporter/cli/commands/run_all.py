"""Run-all command."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ck_exporter.extract_openai import extract_export
from ck_exporter.logging import get_current_log_mode
from ck_exporter.pipeline.compile import compile_docs
from ck_exporter.pipeline.linearize import linearize_export
from ck_exporter.ui.dashboard import PipelineDashboard

console = Console()


def run_all_command(
    input: Path = typer.Option(
        ...,
        "--input",
        "-i",
        help="Path to ChatGPT export JSON (list), single-conversation JSON (mapping/current_node), Claude export JSON, or a directory of per-conversation .json files",
    ),
    evidence_dir: Path = typer.Option(Path("_evidence"), "--evidence", "-e", help="Evidence directory"),
    atoms_dir: Path = typer.Option(Path("_atoms"), "--atoms", "-a", help="Atoms directory"),
    docs_dir: Path = typer.Option(Path("project/docs"), "--docs", "-d", help="Docs directory"),
    fast_model: str = typer.Option(None, "--fast-model", help="Fast model for Pass 1 (default: z-ai/glm-4.7)"),
    big_model: str = typer.Option(None, "--big-model", help="Big model for Pass 2 (default: z-ai/glm-4.7)"),
    max_concurrency: int = typer.Option(None, "--max-concurrency", help="Max concurrent conversations (default: 8)"),
    skip_existing: bool = typer.Option(True, "--skip-existing/--no-skip-existing", help="Skip conversations with existing outputs"),
    use_openrouter: bool = typer.Option(True, "--openrouter/--no-openrouter", help="Use OpenRouter API (default: True)"),
    conversation_id: str = typer.Option(None, "--conversation-id", "-c", help="Process only this conversation ID (for testing)"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Limit number of conversations to process (deterministic: first N by sorted filename)"),
    dashboard: Optional[bool] = typer.Option(
        None,
        "--dashboard/--no-dashboard",
        help="Enable/disable persistent dashboard (default: auto-detect based on TTY and log mode)",
    ),
    dashboard_log_lines: int = typer.Option(50, "--dashboard-log-lines", help="Number of log lines to show in dashboard tail (default: 50)"),
) -> None:
    """Run the full pipeline: linearize → extract → compile."""
    if not input.exists():
        console.print(f"[red]Input path not found: {input}[/red]")
        raise typer.Exit(1)

    # Determine if dashboard should be enabled
    current_log_mode = get_current_log_mode()

    use_dashboard = False
    if dashboard is not None:
        use_dashboard = dashboard
    else:
        # Auto-detect: enable if TTY and not machine mode
        use_dashboard = sys.stderr.isatty() and (current_log_mode != "machine")

    # Create dashboard if enabled
    dashboard_obj: Optional[PipelineDashboard] = None
    if use_dashboard:
        dashboard_obj = PipelineDashboard(
            steps=["Linearize", "Extract", "Compile"],
            log_lines=dashboard_log_lines,
        )
        dashboard_obj.install_log_handler()

        # Suppress normal console handler to prevent log spam
        # (dashboard will show logs in its panel, file handlers still work)
        import logging

        root_logger = logging.getLogger()
        # Remove stderr StreamHandlers (but keep file handlers and dashboard handler)
        handlers_to_remove = [
            h
            for h in root_logger.handlers
            if isinstance(h, logging.StreamHandler)
            and hasattr(h, "stream")
            and h.stream == sys.stderr
            and h != dashboard_obj.log_handler
        ]
        for handler in handlers_to_remove:
            root_logger.removeHandler(handler)

    try:
        if dashboard_obj:
            # Run with dashboard
            with dashboard_obj.run_live():
                # Step 1: Linearize
                dashboard_obj.set_step_status("Linearize", "running")
                linearize_cb = dashboard_obj.get_progress_callback("Linearize")
                linearize_export(input, evidence_dir, limit=limit, progress_cb=linearize_cb)
                dashboard_obj.set_step_status("Linearize", "complete")

                # Step 2: Extract
                dashboard_obj.set_step_status("Extract", "running")
                extract_cb = dashboard_obj.get_progress_callback("Extract")
                extract_export(
                    input,
                    evidence_dir,
                    atoms_dir,
                    fast_model=fast_model,
                    big_model=big_model,
                    max_concurrency=max_concurrency,
                    skip_existing=skip_existing,
                    use_openrouter=use_openrouter,
                    conversation_id=conversation_id,
                    limit=limit,
                    progress_cb=extract_cb,
                )
                dashboard_obj.set_step_status("Extract", "complete")

                # Step 3: Compile
                dashboard_obj.set_step_status("Compile", "running")
                compile_cb = dashboard_obj.get_progress_callback("Compile")
                compile_docs(atoms_dir, docs_dir, progress_cb=compile_cb)
                dashboard_obj.set_step_status("Compile", "complete")
        else:
            # Run without dashboard (original behavior)
            console.print("[bold]Running full pipeline[/bold]")

            # Step 1: Linearize
            console.print("\n[bold cyan]Step 1: Linearizing conversations[/bold cyan]")
            linearize_export(input, evidence_dir, limit=limit)

            # Step 2: Extract
            console.print("\n[bold cyan]Step 2: Extracting knowledge atoms[/bold cyan]")
            extract_export(
                input,
                evidence_dir,
                atoms_dir,
                fast_model=fast_model,
                big_model=big_model,
                max_concurrency=max_concurrency,
                skip_existing=skip_existing,
                use_openrouter=use_openrouter,
                conversation_id=conversation_id,
                limit=limit,
                progress_cb=None,
            )

            # Step 3: Compile
            console.print("\n[bold cyan]Step 3: Compiling documentation[/bold cyan]")
            compile_docs(atoms_dir, docs_dir, progress_cb=None)

            console.print("\n[bold green]✓ Pipeline complete![/bold green]")
    finally:
        if dashboard_obj:
            dashboard_obj.remove_log_handler()
