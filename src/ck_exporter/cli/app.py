"""Main Typer application."""

import os
from pathlib import Path
from typing import Optional

import typer

from ck_exporter.cli.commands import (
    assign_topics_command,
    compile_command,
    consolidate_command,
    discover_topics_command,
    extract_command,
    linearize_command,
    run_all_command,
)
from ck_exporter.logging import configure_logging

app = typer.Typer(help="ChatGPT Conversation Knowledge Exporter")


@app.callback()
def main(
    log_mode: str = typer.Option(
        os.getenv("CKX_LOG_MODE", "auto"),
        "--log-mode",
        help="Logging mode: human (Rich console), hybrid (Rich console + JSON file), machine (JSON file only), or auto (default: human if TTY, hybrid if log-file set)",
    ),
    log_format: str = typer.Option(
        os.getenv("CKX_LOG_FORMAT", "json"),
        "--log-format",
        help="Log format: json, rich, or plain (used when mode is not specified, for backward compatibility)",
    ),
    log_level: str = typer.Option(
        os.getenv("CKX_LOG_LEVEL", "INFO"),
        "--log-level",
        help="Log level: DEBUG, INFO, WARNING, ERROR",
    ),
    log_file: Optional[Path] = typer.Option(
        os.getenv("CKX_LOG_FILE") if os.getenv("CKX_LOG_FILE") else None,
        "--log-file",
        help="Optional file path to write logs to (JSON format)",
    ),
    third_party_log_level: str = typer.Option(
        os.getenv("CKX_THIRD_PARTY_LOG_LEVEL", "WARNING"),
        "--third-party-log-level",
        help="Log level for third-party libraries: WARNING, ERROR, INFO",
    ),
    hybrid_ui: bool = typer.Option(
        os.getenv("CKX_HYBRID_UI", "true").lower() == "true",
        "--hybrid-ui/--no-hybrid-ui",
        help="Enable hybrid UI mode (Rich banners + structured logs)",
    ),
) -> None:
    """Configure logging before command execution."""
    configure_logging(
        level=log_level,
        format=log_format,
        log_file=log_file,
        third_party_level=third_party_log_level,
        hybrid_ui=hybrid_ui,
        mode=log_mode,  # type: ignore
    )


# Register commands with explicit names
app.command(name="linearize")(linearize_command)
app.command(name="extract")(extract_command)
app.command(name="compile")(compile_command)
app.command(name="consolidate")(consolidate_command)
app.command(name="run-all")(run_all_command)
app.command(name="discover-topics")(discover_topics_command)
app.command(name="assign-topics")(assign_topics_command)
