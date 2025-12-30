"""Persistent Rich terminal dashboard for pipeline progress."""

import logging
import sys
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable, Deque, Dict, Optional

from rich.console import Console, RenderableType
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

try:
    from rich.logging import RichHandler
except ImportError:
    RichHandler = None


@dataclass
class StepStatus:
    """Status for a pipeline step."""

    name: str
    status: str = "pending"  # pending, running, complete, error
    completed: int = 0
    total: int = 0
    start_time: Optional[float] = None
    elapsed: float = 0.0
    rate: float = 0.0
    eta: Optional[float] = None
    current_item: Optional[str] = None


class DashboardLogHandler(logging.Handler):
    """Log handler that captures logs into a ring buffer for dashboard display."""

    def __init__(self, ring_buffer_size: int = 100):
        super().__init__()
        self.ring_buffer: Deque[str] = deque(maxlen=ring_buffer_size)
        self.console = Console(stderr=True, width=120)

    def emit(self, record: logging.LogRecord) -> None:
        """Format and store log record in ring buffer."""
        try:
            # Format as human-readable (not JSON)
            level_name = record.levelname
            logger_name = record.name.split(".")[-1]  # Just the module name
            message = record.getMessage()

            # Color coding
            if level_name == "ERROR":
                formatted = f"[red]{level_name:8}[/red] {logger_name}: {message}"
            elif level_name == "WARNING":
                formatted = f"[yellow]{level_name:8}[/yellow] {logger_name}: {message}"
            elif level_name == "INFO":
                formatted = f"[cyan]{level_name:8}[/cyan] {logger_name}: {message}"
            elif level_name == "DEBUG":
                formatted = f"[dim]{level_name:8}[/dim] {logger_name}: {message}"
            else:
                formatted = f"{level_name:8} {logger_name}: {message}"

            # Add exception traceback if present
            if record.exc_info:
                formatted += "\n" + self.format(record)

            self.ring_buffer.append(formatted)
        except Exception:
            # Don't let logging errors break the dashboard
            pass

    def get_recent_logs(self, max_lines: int = 50) -> list[str]:
        """Get the most recent log lines."""
        return list(self.ring_buffer)[-max_lines:]


class PipelineDashboard:
    """Persistent terminal dashboard showing pipeline progress."""

    def __init__(self, steps: list[str], log_lines: int = 50):
        """
        Initialize dashboard.

        Args:
            steps: List of step names (e.g., ["Linearize", "Extract", "Compile"])
            log_lines: Number of log lines to show in tail panel
        """
        self.steps: Dict[str, StepStatus] = {name: StepStatus(name=name) for name in steps}
        self.log_lines = log_lines
        self.log_handler: Optional[DashboardLogHandler] = None
        self.console = Console(stderr=True)
        self.start_time = time.time()
        self.overall_elapsed = 0.0

    def set_step_total(self, step_name: str, total: int) -> None:
        """Set total count for a step."""
        if step_name in self.steps:
            self.steps[step_name].total = total
            if self.steps[step_name].start_time is None:
                self.steps[step_name].start_time = time.time()

    def update_step_progress(
        self, step_name: str, completed: int, current_item: Optional[str] = None, total: Optional[int] = None
    ) -> None:
        """Update progress for a step."""
        if step_name not in self.steps:
            return

        step = self.steps[step_name]
        step.completed = completed
        step.current_item = current_item
        
        # Update total if provided
        if total is not None and total > 0:
            step.total = total
            if step.start_time is None:
                step.start_time = time.time()

        if step.start_time is not None:
            step.elapsed = time.time() - step.start_time
            if step.elapsed > 0 and step.total > 0:
                step.rate = step.completed / step.elapsed
                remaining = step.total - step.completed
                if step.rate > 0:
                    step.eta = remaining / step.rate
                else:
                    step.eta = None

    def set_step_status(self, step_name: str, status: str) -> None:
        """Set status for a step (pending, running, complete, error)."""
        if step_name in self.steps:
            self.steps[step_name].status = status
            if status == "running" and self.steps[step_name].start_time is None:
                self.steps[step_name].start_time = time.time()
            elif status in ("complete", "error"):
                # Finalize elapsed time
                if self.steps[step_name].start_time is not None:
                    self.steps[step_name].elapsed = time.time() - self.steps[step_name].start_time

    def _format_time(self, seconds: Optional[float]) -> str:
        """Format seconds as human-readable time."""
        if seconds is None:
            return "—"
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"

    def _create_status_table(self) -> Table:
        """Create status table showing all steps."""
        table = Table(show_header=True, header_style="bold", box=None, padding=(0, 1))
        table.add_column("Step", style="cyan", width=12)
        table.add_column("Status", width=10)
        table.add_column("Progress", width=20)
        table.add_column("Elapsed", width=10, justify="right")
        table.add_column("Rate", width=10, justify="right")
        table.add_column("ETA", width=10, justify="right")

        for step_name, step in self.steps.items():
            # Status icon
            if step.status == "complete":
                status_icon = "[green]✓[/green]"
            elif step.status == "running":
                status_icon = "[yellow]⠋[/yellow]"
            elif step.status == "error":
                status_icon = "[red]✗[/red]"
            else:
                status_icon = "[dim]○[/dim]"

            # Progress
            if step.total > 0:
                progress_text = f"{step.completed}/{step.total}"
                if step.current_item:
                    # Truncate long item names
                    item = step.current_item[:30] + "..." if len(step.current_item) > 30 else step.current_item
                    progress_text += f" ({item})"
            else:
                progress_text = "—"

            # Elapsed
            elapsed_text = self._format_time(step.elapsed if step.status != "pending" else None)

            # Rate
            if step.rate > 0:
                rate_text = f"{step.rate:.2f}/s"
            else:
                rate_text = "—"

            # ETA
            eta_text = self._format_time(step.eta)

            table.add_row(step_name, status_icon, progress_text, elapsed_text, rate_text, eta_text)

        return table

    def _create_progress_bars(self) -> Progress:
        """Create Rich Progress bars for active steps."""
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console,
        )

        for step_name, step in self.steps.items():
            if step.status == "running" and step.total > 0:
                task_id = progress.add_task(
                    f"{step_name}...",
                    total=step.total,
                    completed=step.completed,
                )
                # Store task_id for updates (we'll use step_name as key)
                step._task_id = task_id  # type: ignore

        return progress

    def _create_log_panel(self) -> Panel:
        """Create panel showing recent log lines."""
        if self.log_handler:
            logs = self.log_handler.get_recent_logs(self.log_lines)
            log_text = "\n".join(logs) if logs else "[dim]No logs yet...[/dim]"
        else:
            log_text = "[dim]Logs not initialized...[/dim]"

        return Panel(
            log_text,
            title="[bold]Recent Logs[/bold]",
            border_style="blue",
            height=min(self.log_lines + 2, 20),  # Cap height
        )

    def render(self) -> RenderableType:
        """Render the complete dashboard."""
        self.overall_elapsed = time.time() - self.start_time

        # Create layout
        layout = Layout()

        # Top: Status table
        status_table = self._create_status_table()
        status_panel = Panel(
            status_table,
            title=f"[bold]CKX Pipeline[/bold] • {self._format_time(self.overall_elapsed)} elapsed",
            border_style="green",
        )

        # Middle: Progress bars (only for running steps)
        progress_bars = self._create_progress_bars()
        progress_panel = Panel(progress_bars, border_style="yellow", height=5)

        # Bottom: Log tail
        log_panel = self._create_log_panel()

        # Arrange vertically
        layout.split_column(
            Layout(status_panel, name="status", size=8),
            Layout(progress_panel, name="progress", size=7),
            Layout(log_panel, name="logs"),
        )

        return layout

    def install_log_handler(self) -> None:
        """Install log handler to capture logs."""
        if self.log_handler is None:
            self.log_handler = DashboardLogHandler(ring_buffer_size=self.log_lines * 2)
            root_logger = logging.getLogger()
            root_logger.addHandler(self.log_handler)

    def remove_log_handler(self) -> None:
        """Remove log handler."""
        if self.log_handler:
            root_logger = logging.getLogger()
            root_logger.removeHandler(self.log_handler)
            self.log_handler = None

    def get_progress_callback(self, step_name: str) -> Callable[[int, int, Optional[dict]], None]:
        """Get a progress callback function for a step."""

        def callback(completed: int, total: int, context: Optional[dict] = None) -> None:
            if context is None:
                context = {}
            current_item = context.get("conversation_id") if context else None
            # Update total on first call or when it changes
            if total > 0:
                self.set_step_total(step_name, total)
            self.update_step_progress(step_name, completed, current_item, total=total if total > 0 else None)

        return callback

    def run_live(self, refresh_per_second: float = 4.0) -> Live:
        """Create Live context for updating dashboard."""
        return Live(
            self,  # Pass self as the renderable, not self.render()
            console=self.console,
            refresh_per_second=refresh_per_second,
            screen=False,
        )
    
    def __rich__(self) -> RenderableType:
        """Rich protocol: render the dashboard."""
        return self.render()
