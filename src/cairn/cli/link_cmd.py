"""`cairn link [<project-repo>]` — pair a project repo with a cairn.

Writes a ``cairn.toml`` at the project repo root so agents working inside
the project repo can discover the paired cairn via cwd-walk. See ADR-0006,
ADR-0010, and ADR-0012.

Three modes:
- ``--name <handle>`` (local-registry): looks up the cairn in the user's
  local MCP registry. Run from anywhere — typically inside the project repo.
- No flags (local-path fallback): resolves the cairn from cwd-walk.
  Run from inside the cairn directory.
- ``--endpoint <url> --name <handle>`` (remote-MCP): records an HTTP MCP
  server URL plus the cairn's handle on that server. Pairing travels with
  the repo; credentials do not.
"""

from __future__ import annotations

from pathlib import Path

import typer

from ..cairn_toml import POINTER_FILE, CairnTomlError, write_pointer
from ..mcp.remote import probe
from ..paths import is_cairn_root, resolve_cairn
from ..registry import lookup
from ._common import resolve_or_exit


def link(
    project_repo: Path = typer.Argument(
        None,
        help=(
            "Path to the project repo to pair with the cairn. "
            "Defaults to the current working directory."
        ),
    ),
    name: str | None = typer.Option(
        None,
        "--name",
        help=(
            "The cairn handle. For local-registry mode: the name you used with "
            "`cairn register <handle> <path>`. For remote-MCP mode (with "
            "--endpoint): the cairn handle on the remote server. "
            "If omitted and --endpoint is not given, the cairn is linked by "
            "relative path from the cairn directory."
        ),
    ),
    endpoint: str | None = typer.Option(
        None,
        "--endpoint",
        help=(
            "HTTP MCP server URL for remote-MCP mode (e.g. "
            "https://mcp.example.com/mcp). Must be combined with --name. "
            "Pairing is stored in cairn.toml (safe to commit). "
            "Credentials are stored separately — see CAIRN_BEARER_TOKEN "
            "or ~/.config/cairn/credentials.toml."
        ),
    ),
    no_probe: bool = typer.Option(
        False,
        "--no-probe",
        help="Skip the connectivity check before writing the pointer (remote-MCP mode).",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite an existing cairn.toml at the project repo root.",
    ),
) -> None:
    """Pair a project repo with a cairn by writing a cairn.toml pointer."""
    project = (project_repo or Path.cwd()).resolve()
    if not project.is_dir():
        typer.echo(f"error: project-repo path is not a directory: {project}", err=True)
        raise typer.Exit(code=1)
    target = project / POINTER_FILE
    if target.exists() and not force:
        typer.echo(
            f"error: {target} already exists. Pass --force to overwrite.", err=True
        )
        raise typer.Exit(code=1)

    # --- Remote-MCP mode: --endpoint + --name --------------------------------
    if endpoint is not None:
        if name is None:
            typer.echo(
                "error: --endpoint requires --name (the cairn handle on the remote server).",
                err=True,
            )
            raise typer.Exit(code=1)

        if not no_probe:
            reachable = probe(endpoint, timeout=10)
            if not reachable:
                typer.echo(
                    f"error: could not reach {endpoint}. "
                    f"Check the URL and network, or pass --no-probe to skip this check.",
                    err=True,
                )
                raise typer.Exit(code=1)

        try:
            written = write_pointer(project, endpoint=endpoint, name=name)
        except CairnTomlError as exc:
            typer.echo(f"error: {exc}", err=True)
            raise typer.Exit(code=1) from None

        typer.echo(f"Linked {project} → remote cairn '{name}' at {endpoint}.")
        typer.echo(f"Wrote {written}.")
        typer.echo(
            "\nCredentials are NOT stored in cairn.toml. Set them via:\n"
            "  export CAIRN_BEARER_TOKEN=<your-token>   # env var (any session)\n"
            "  # or add to ~/.config/cairn/credentials.toml:\n"
            f'  [endpoints."{endpoint}"]\n'
            "  token = \"<your-token>\"\n"
            "\nTo register the remote server with Claude Code:\n"
            f"  claude mcp add cairn-remote -- cairn mcp --transport streamable-http\n"
            "  # or point directly at the remote if it's always-on:\n"
            f"  claude mcp add cairn-remote <URL>"
        )
        return

    # --- Local-registry mode: --name only ------------------------------------
    if name is not None:
        existing = lookup(name)
        if existing is None:
            typer.echo(
                f"error: '{name}' is not registered. Add it first with "
                f"`cairn register {name} <path-to-cairn>`, then re-run link. "
                f"Listed registry: `cairn registered`.",
                err=True,
            )
            raise typer.Exit(code=1)
        try:
            written = write_pointer(project, name=name)
        except CairnTomlError as exc:
            typer.echo(f"error: {exc}", err=True)
            raise typer.Exit(code=1) from None
        typer.echo(
            f"Linked {project} → cairn '{name}' (at {existing.path}). "
            f"Wrote {written}."
        )
        typer.echo(
            "\nFor agents in Claude Code sessions opened here to reach the "
            "cairn, the cairn MCP server must be registered with Claude Code "
            "(one-time, ever):\n"
            "  claude mcp add cairn cairn mcp\n"
            "Then restart any open Claude Code sessions to pick it up."
        )
        return

    # --- Local-path fallback: no flags, cwd-walk to find cairn ---------------
    try:
        cairn_paths = resolve_or_exit()
    except SystemExit:
        typer.echo(
            "hint: pass --name <registered-cairn> to link without being inside "
            "the cairn directory. See `cairn registered`.",
            err=True,
        )
        raise typer.Exit(code=2) from None

    if project == cairn_paths.root.resolve():
        typer.echo(
            f"error: refusing to link a cairn ({cairn_paths.root}) to itself. "
            f"Did you mean to pass a separate project-repo path?",
            err=True,
        )
        raise typer.Exit(code=1)

    if not is_cairn_root(cairn_paths.root):
        typer.echo(f"error: {cairn_paths.root} is not a cairn root", err=True)
        raise typer.Exit(code=1)
    try:
        written = write_pointer(project, path=cairn_paths.root)
    except CairnTomlError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=1) from None
    typer.echo(f"Linked {project} → {cairn_paths.root}. Wrote {written}.")
    typer.echo(
        "\nFor agents in Claude Code sessions opened here to reach the "
        "cairn, the cairn MCP server must be registered with Claude Code "
        "(one-time, ever):\n"
        "  claude mcp add cairn cairn mcp\n"
        "Then restart any open Claude Code sessions to pick it up."
    )


# Silence unused-import linting (resolve_cairn imported for potential future use).
_ = resolve_cairn
