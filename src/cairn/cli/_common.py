"""Shared helpers for CLI subcommands."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from ..errors import CairnError, NotACairnError
from ..paths import CairnPaths, resolve_cairn


def resolve_or_exit(start: Path | None = None) -> CairnPaths:
    """Resolve the enclosing cairn or exit with a clear message."""
    try:
        return resolve_cairn(start)
    except NotACairnError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=2) from None


def exit_on(error: CairnError, code: int = 1) -> None:
    typer.echo(f"error: {error}", err=True)
    sys.exit(code)
