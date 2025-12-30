"""Unified logging configuration for ck_exporter.

This module provides structured logging with JSON output by default,
context helpers, and third-party log level controls.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Literal, Optional

try:
    from rich.logging import RichHandler
except ImportError:
    RichHandler = None

# Global state to track current logging mode
_current_mode: Optional[str] = None


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add event type if present
        if hasattr(record, "event"):
            log_data["event"] = record.event

        # Add all extra fields
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
                "event",
            }:
                log_data[key] = value

        # Add exception info if present
        if record.exc_info:
            exc_type, exc_value, exc_traceback = record.exc_info
            log_data["exception"] = {
                "type": exc_type.__name__ if exc_type else None,
                "message": str(exc_value) if exc_value else None,
                "traceback": self.formatException(record.exc_info) if exc_traceback else None,
            }

        return json.dumps(log_data, ensure_ascii=False)


class PlainFormatter(logging.Formatter):
    """Plain text formatter for simple log output."""

    def __init__(self):
        super().__init__(fmt="%(levelname)s %(name)s: %(message)s")

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as plain text."""
        msg = super().format(record)
        if record.exc_info:
            msg += "\n" + self.formatException(record.exc_info)
        return msg


def get_current_log_mode() -> Optional[str]:
    """Get the current logging mode."""
    return _current_mode


def should_show_progress() -> bool:
    """
    Determine if Rich progress bars/spinners should be shown.

    Returns:
        True if progress should be shown (interactive mode), False otherwise
    """
    global _current_mode
    if _current_mode is None:
        # Default: show progress if stderr is a TTY
        return sys.stderr.isatty()
    
    # human and hybrid modes show progress if interactive
    if _current_mode in ("human", "hybrid"):
        return sys.stderr.isatty()
    
    # machine mode never shows progress
    return False


def configure_logging(
    level: str = "INFO",
    format: str = "json",  # noqa: A002
    log_file: Optional[Path] = None,
    third_party_level: str = "WARNING",
    hybrid_ui: bool = True,
    mode: Literal["human", "hybrid", "machine", "auto"] = "auto",
) -> None:
    """
    Configure logging for ck_exporter.

    Args:
        level: Log level for ck_exporter modules (DEBUG, INFO, WARNING, ERROR)
        format: Log format (json, rich, plain) - used when mode is not specified
        log_file: Optional file path to write logs to
        third_party_level: Log level for third-party libraries (default WARNING)
        hybrid_ui: If True, RichHandler will use stderr (for hybrid UI mode)
        mode: Logging mode (human/hybrid/machine/auto). If 'auto', determines based on TTY and log_file.
            - human: Rich console logs to stderr (default for interactive)
            - hybrid: Rich console logs to stderr + JSON logs to file
            - machine: JSON logs to file only (no console output)
            - auto: human if TTY, hybrid if log_file set, otherwise plain
    """
    global _current_mode
    
    # Resolve auto mode
    if mode == "auto":
        if sys.stderr.isatty():
            mode = "human"
        elif log_file:
            mode = "hybrid"
        else:
            mode = "human"  # Default to human even if not TTY
    
    _current_mode = mode
    
    # Convert level strings to logging constants
    log_level = getattr(logging, level.upper(), logging.INFO)
    third_party_log_level = getattr(logging, third_party_level.upper(), logging.WARNING)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Determine console format based on mode
    if mode == "machine":
        # Machine mode: no console output, only file (if specified)
        console_format = None
    elif mode == "hybrid":
        # Hybrid mode: Rich console + JSON file
        console_format = "rich"
    elif mode == "human":
        # Human mode: Rich console (or plain if rich not available)
        console_format = "rich"
    else:
        # Fallback to format parameter for backward compatibility
        console_format = format

    # Create console handler based on mode/format
    if console_format == "json":
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(JsonFormatter())
    elif console_format == "rich":
        if RichHandler is None:
            # Fallback to plain if rich not available
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(PlainFormatter())
        else:
            handler = RichHandler(
                console=None,  # Use default console
                show_path=False,
                rich_tracebacks=True,
                show_time=True,
            )
            # RichHandler writes to stderr by default, which is what we want
    elif console_format == "plain":
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(PlainFormatter())
    else:
        # No console handler for machine mode (unless log_file not set, then use plain)
        handler = None

    if handler:
        handler.setLevel(log_level)
        root_logger.addHandler(handler)

    # Add file handler if specified (always JSON in file)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(JsonFormatter())
        file_handler.setLevel(log_level)
        root_logger.addHandler(file_handler)
    elif mode == "machine":
        # Machine mode requires a log file
        # If not provided, fall back to stderr with JSON
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(JsonFormatter())
        handler.setLevel(log_level)
        root_logger.addHandler(handler)

    # Configure third-party loggers to be quieter
    third_party_loggers = [
        "bertopic",
        "hdbscan",
        "umap",
        "numba",
        "openai",
        "httpx",
        "urllib3",
        "httpcore",
    ]
    for logger_name in third_party_loggers:
        third_party_logger = logging.getLogger(logger_name)
        third_party_logger.setLevel(third_party_log_level)
        # Prevent propagation to root if we want complete control
        # third_party_logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


__all__ = [
    "configure_logging",
    "get_logger",
    "with_context",
    "should_show_progress",
    "get_current_log_mode",
    "JsonFormatter",
    "PlainFormatter",
]


def with_context(logger: logging.Logger, **fields: Any) -> logging.LoggerAdapter:
    """
    Create a logger adapter with context fields.

    Args:
        logger: Base logger
        **fields: Context fields to include in all log records

    Returns:
        LoggerAdapter with context fields

    Example:
        logger = get_logger(__name__)
        conv_logger = with_context(logger, conversation_id="abc123", stage="extract")
        conv_logger.info("Processing chunk", extra={"chunk_num": 1})
    """
    return logging.LoggerAdapter(logger, fields)
