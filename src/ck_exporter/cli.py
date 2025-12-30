"""CLI entrypoint shim for backward compatibility.

This module re-exports the app from the new cli package structure.
"""

from ck_exporter.cli import app

__all__ = ["app"]
