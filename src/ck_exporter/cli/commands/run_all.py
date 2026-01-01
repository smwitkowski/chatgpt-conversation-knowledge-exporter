"""Run-all command."""

import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import typer
from rich.console import Console

from ck_exporter.extract_openai import extract_export
from ck_exporter.logging import get_current_log_mode
from ck_exporter.pipeline.compile import compile_docs
from ck_exporter.pipeline.linearize import linearize_export
from ck_exporter.ui.dashboard import PipelineDashboard

console = Console()

# Type detection aliases
_DOC_DIR_ALIASES = {
    "documents",
    "document",
    "docs",
}

_MEETING_DIR_ALIASES = {
    "meeting_artifacts",
    "meeting_artifact",
    "meeting",
    "meetings",
    "meeting_notes",
    "meeting_notes_and_transcripts",
    "meeting_transcripts",
}

_AI_DIR_ALIASES = {
    "ai_conversations",
    "ai_conversation",
    "ai",
    "conversations",
    "chatgpt_conversations",
    "chatgpt_conversation",
    "claude_conversations",
}


def _norm_token(s: str) -> str:
    """Normalize a string to a filesystem-safe token."""
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def _discover_typed_inputs(root: Path) -> List[Tuple[str, Path]]:
    """
    Discover known subdirectories under `root` and label them by type key.
    
    Returns:
        List of (type_key, subdir_path) tuples where type_key is one of:
        - "documents"
        - "meetings"
        - "ai"
    """
    if not root.is_dir():
        return []

    found: List[Tuple[str, Path]] = []
    for p in sorted([d for d in root.iterdir() if d.is_dir()], key=lambda x: x.name.lower()):
        name = _norm_token(p.name)

        if name in _DOC_DIR_ALIASES:
            found.append(("documents", p))
        elif name in _MEETING_DIR_ALIASES:
            found.append(("meetings", p))
        elif name in _AI_DIR_ALIASES:
            found.append(("ai", p))

    # Deterministic order: documents -> meetings -> ai
    order = {"documents": 0, "meetings": 1, "ai": 2}
    found.sort(key=lambda t: order.get(t[0], 99))
    return found


def _derive_output_dirs_from_input(input_path: Path) -> Tuple[Path, Path, Path]:
    """
    Derive dedicated output directories from input directory name.
    
    For input like `_sources/Schreiber`, creates:
    - `_evidence_schreiber`
    - `_atoms_schreiber`
    - `output/schreiber/docs`
    """
    # Get the directory name (last component of path) and sanitize for filesystem
    dir_name = _norm_token(input_path.name)
    
    # Create output directories based on directory name
    evidence_dir = Path(f"_evidence_{dir_name}")
    atoms_dir = Path(f"_atoms_{dir_name}")
    docs_dir = Path(f"output/{dir_name}/docs")
    
    return evidence_dir, atoms_dir, docs_dir


def _derive_output_dirs(dataset_root: Path, type_key: str) -> Tuple[Path, Path, Path]:
    """
    Derive output directories for a specific type under a dataset.
    
    For input like `_sources/Schreiber` and type_key "meetings", creates:
    - `_evidence_schreiber_meetings`
    - `_atoms_schreiber_meetings`
    - `output/schreiber/meetings/docs`
    """
    dataset = _norm_token(dataset_root.name)
    type_slug = _norm_token(type_key)
    evidence_dir = Path(f"_evidence_{dataset}_{type_slug}")
    atoms_dir = Path(f"_atoms_{dataset}_{type_slug}")
    docs_dir = Path(f"output/{dataset}/{type_slug}/docs")
    return evidence_dir, atoms_dir, docs_dir


def _run_pipeline(
    *,
    input_path: Path,
    evidence_dir: Path,
    atoms_dir: Path,
    docs_dir: Path,
    input_kind: str,
    fast_model: Optional[str],
    big_model: Optional[str],
    max_concurrency: Optional[int],
    skip_existing: bool,
    use_openrouter: bool,
    conversation_id: Optional[str],
    limit: Optional[int],
    dashboard_obj: Optional[PipelineDashboard],
) -> None:
    """
    Run the 3-step pipeline: linearize → extract → compile.
    
    This is a reusable helper that handles both dashboard and non-dashboard modes.
    """
    if dashboard_obj:
        # Run with dashboard
        with dashboard_obj.run_live():
            # Step 1: Linearize
            dashboard_obj.set_step_status("Linearize", "running")
            linearize_cb = dashboard_obj.get_progress_callback("Linearize")
            linearize_export(input_path, evidence_dir, limit=limit, progress_cb=linearize_cb, non_json_kind=input_kind)
            dashboard_obj.set_step_status("Linearize", "complete")

            # Step 2: Extract
            dashboard_obj.set_step_status("Extract", "running")
            extract_cb = dashboard_obj.get_progress_callback("Extract")
            extract_export(
                input_path,
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
                non_json_kind=input_kind,
            )
            dashboard_obj.set_step_status("Extract", "complete")

            # Step 3: Compile
            dashboard_obj.set_step_status("Compile", "running")
            compile_cb = dashboard_obj.get_progress_callback("Compile")
            compile_docs(atoms_dir, docs_dir, progress_cb=compile_cb)
            dashboard_obj.set_step_status("Compile", "complete")
    else:
        # Run without dashboard
        console.print("[bold]Running full pipeline[/bold]")

        # Step 1: Linearize
        console.print("\n[bold cyan]Step 1: Linearizing conversations[/bold cyan]")
        linearize_export(input_path, evidence_dir, limit=limit, non_json_kind=input_kind)

        # Step 2: Extract
        console.print("\n[bold cyan]Step 2: Extracting knowledge atoms[/bold cyan]")
        extract_export(
            input_path,
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
            non_json_kind=input_kind,
        )

        # Step 3: Compile
        console.print("\n[bold cyan]Step 3: Compiling documentation[/bold cyan]")
        compile_docs(atoms_dir, docs_dir, progress_cb=None)

        console.print("\n[bold green]✓ Pipeline complete![/bold green]")


def run_all_command(
    input: Path = typer.Option(
        ...,
        "--input",
        "-i",
        help="Path to ChatGPT export JSON (list), single-conversation JSON (mapping/current_node), Claude export JSON, or a directory of per-conversation .json files",
    ),
    evidence_dir: Optional[Path] = typer.Option(None, "--evidence", "-e", help="Evidence directory (auto-derived from input directory name if not specified)"),
    atoms_dir: Optional[Path] = typer.Option(None, "--atoms", "-a", help="Atoms directory (auto-derived from input directory name if not specified)"),
    docs_dir: Optional[Path] = typer.Option(None, "--docs", "-d", help="Docs directory (auto-derived from input directory name if not specified)"),
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
    input_kind: str = typer.Option("meeting", "--input-kind", help="How to interpret non-JSON files: meeting|document (default: meeting)"),
    split_by_subdir: bool = typer.Option(
        True,
        "--split-by-subdir/--no-split-by-subdir",
        help="If input is a directory containing known subfolders (documents/meeting_artifacts/ai-conversations), run once per subfolder and split output trees.",
    ),
    unified_output: bool = typer.Option(
        False,
        "--unified-output/--no-unified-output",
        help="When splitting by subdirectory, write all outputs to the same directories (unified) instead of separate per-type directories.",
    ),
) -> None:
    """Run the full pipeline: linearize → extract → compile."""
    if not input.exists():
        console.print(f"[red]Input path not found: {input}[/red]")
        raise typer.Exit(1)

    if input_kind not in ("meeting", "document"):
        console.print(f"[red]Invalid input-kind: {input_kind}. Must be 'meeting' or 'document'[/red]")
        raise typer.Exit(1)

    if input_kind == "document" and not input.is_dir():
        console.print(f"[red]Document mode requires a directory input, got: {input}[/red]")
        raise typer.Exit(1)

    # Determine if dashboard should be enabled
    current_log_mode = get_current_log_mode()
    use_dashboard = False
    if dashboard is not None:
        use_dashboard = dashboard
    else:
        # Auto-detect: enable if TTY and not machine mode
        use_dashboard = sys.stderr.isatty() and (current_log_mode != "machine")

    # Split-by-subdir mode (directory only)
    if input.is_dir() and split_by_subdir:
        typed = _discover_typed_inputs(input)
        if typed:
            if unified_output:
                console.print(f"[bold]Running split pipeline with unified outputs[/bold] ({len(typed)} subfolder(s))")
                # Derive unified output dirs (same for all types)
                if evidence_dir is None or atoms_dir is None or docs_dir is None:
                    derived_evidence, derived_atoms, derived_docs = _derive_output_dirs_from_input(input)
                    unified_evidence = evidence_dir or derived_evidence
                    unified_atoms = atoms_dir or derived_atoms
                    unified_docs = docs_dir or derived_docs
                else:
                    unified_evidence = evidence_dir
                    unified_atoms = atoms_dir
                    unified_docs = docs_dir
                console.print(f"[dim]Unified outputs:[/dim]")
                console.print(f"  Evidence: {unified_evidence}")
                console.print(f"  Atoms: {unified_atoms}")
                console.print(f"  Docs: {unified_docs}")
            else:
                console.print(f"[bold]Running split pipeline[/bold] ({len(typed)} subfolder(s))")
            
            for type_key, subdir in typed:
                # Pick parsing mode for non-JSON files
                sub_input_kind = "document" if type_key == "documents" else "meeting"

                if unified_output:
                    # Use unified output directories for all types
                    eff_evidence = unified_evidence
                    eff_atoms = unified_atoms
                    eff_docs = unified_docs
                else:
                    # Derive output dirs (or nest under user-provided dirs)
                    if evidence_dir is None or atoms_dir is None or docs_dir is None:
                        derived_evidence, derived_atoms, derived_docs = _derive_output_dirs(input, type_key)
                        eff_evidence_base = evidence_dir or derived_evidence
                        eff_atoms_base = atoms_dir or derived_atoms
                        eff_docs_base = docs_dir or derived_docs
                    else:
                        eff_evidence_base = evidence_dir
                        eff_atoms_base = atoms_dir
                        eff_docs_base = docs_dir

                    # If user provided explicit dirs, split into subfolders; if derived, they're already split.
                    if evidence_dir is not None:
                        eff_evidence = eff_evidence_base / type_key
                    else:
                        eff_evidence = eff_evidence_base

                    if atoms_dir is not None:
                        eff_atoms = eff_atoms_base / type_key
                    else:
                        eff_atoms = eff_atoms_base

                    if docs_dir is not None:
                        eff_docs = eff_docs_base / type_key
                    else:
                        eff_docs = eff_docs_base

                console.print(f"\n[bold magenta]=== {type_key} ===[/bold magenta]")
                console.print(f"[dim]Input:[/dim] {subdir}")
                console.print(f"[dim]Evidence:[/dim] {eff_evidence}")
                console.print(f"[dim]Atoms:[/dim] {eff_atoms}")
                console.print(f"[dim]Docs:[/dim] {eff_docs}")

                dashboard_obj: Optional[PipelineDashboard] = None
                if use_dashboard:
                    dashboard_obj = PipelineDashboard(
                        steps=["Linearize", "Extract", "Compile"], log_lines=dashboard_log_lines
                    )
                    dashboard_obj.install_log_handler()

                    # Suppress normal console handler to prevent log spam
                    import logging

                    root_logger = logging.getLogger()
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
                    _run_pipeline(
                        input_path=subdir,
                        evidence_dir=eff_evidence,
                        atoms_dir=eff_atoms,
                        docs_dir=eff_docs,
                        input_kind=sub_input_kind,
                        fast_model=fast_model,
                        big_model=big_model,
                        max_concurrency=max_concurrency,
                        skip_existing=skip_existing,
                        use_openrouter=use_openrouter,
                        conversation_id=conversation_id,
                        limit=limit,
                        dashboard_obj=dashboard_obj,
                    )
                finally:
                    if dashboard_obj:
                        dashboard_obj.remove_log_handler()

            console.print("\n[bold green]✓ Split pipeline complete![/bold green]")
            return

    # Fallback: original single-run behavior
    # Auto-derive output directories from input directory name if not explicitly provided
    if input.is_dir():
        if evidence_dir is None or atoms_dir is None or docs_dir is None:
            derived_evidence, derived_atoms, derived_docs = _derive_output_dirs_from_input(input)
            if evidence_dir is None:
                evidence_dir = derived_evidence
            if atoms_dir is None:
                atoms_dir = derived_atoms
            if docs_dir is None:
                docs_dir = derived_docs
            console.print(f"[dim]Auto-derived output directories:[/dim]")
            console.print(f"  Evidence: {evidence_dir}")
            console.print(f"  Atoms: {atoms_dir}")
            console.print(f"  Docs: {docs_dir}")
    else:
        # For file inputs, use defaults if not specified
        if evidence_dir is None:
            evidence_dir = Path("_evidence")
        if atoms_dir is None:
            atoms_dir = Path("_atoms")
        if docs_dir is None:
            docs_dir = Path("output/project/docs")

    # Create dashboard if enabled
    dashboard_obj: Optional[PipelineDashboard] = None
    if use_dashboard:
        dashboard_obj = PipelineDashboard(
            steps=["Linearize", "Extract", "Compile"],
            log_lines=dashboard_log_lines,
        )
        dashboard_obj.install_log_handler()

        # Suppress normal console handler to prevent log spam
        import logging

        root_logger = logging.getLogger()
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
        _run_pipeline(
            input_path=input,
            evidence_dir=evidence_dir,
            atoms_dir=atoms_dir,
            docs_dir=docs_dir,
            input_kind=input_kind,
            fast_model=fast_model,
            big_model=big_model,
            max_concurrency=max_concurrency,
            skip_existing=skip_existing,
            use_openrouter=use_openrouter,
            conversation_id=conversation_id,
            limit=limit,
            dashboard_obj=dashboard_obj,
        )
    finally:
        if dashboard_obj:
            dashboard_obj.remove_log_handler()
