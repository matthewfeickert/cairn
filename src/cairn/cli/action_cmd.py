"""`cairn action add` and `cairn action complete` — manage action items."""

from __future__ import annotations

from datetime import date, datetime, timezone

import typer
from git import Repo
from pydantic import ValidationError

from ..errors import CairnError
from ..git_ops import commit, get_user_identity
from ..ids import next_id
from ..io.state_io import load_state, write_actions
from ..schemas import ActionItem
from ._common import RemoteTarget, resolve_target

app = typer.Typer(no_args_is_help=True, help="Manage action items.")


def _parse_due(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise typer.BadParameter(f"--due-date must be YYYY-MM-DD: {exc}") from exc


@app.command(name="add")
def add(
    assignee: str = typer.Option(..., "--assignee", help="Collaborator id of the assignee."),
    text: str = typer.Option(..., "--text", help="What needs to be done."),
    due_date: str | None = typer.Option(
        None, "--due-date", help="Calendar date YYYY-MM-DD (optional)."
    ),
    related: list[str] = typer.Option(
        [], "--related", help="Repeatable; IDs of related entities (Q-NNN, D-NNN, …)."
    ),
) -> None:
    """Add an action item to ``state/action_items.yaml``."""
    target = resolve_target()

    # --- Remote-MCP dispatch (US-P-13) ---------------------------------------
    if isinstance(target, RemoteTarget):
        _add_remote(target, assignee=assignee, text=text, due_date=due_date, related=related)
        return

    # --- Local dispatch ------------------------------------------------------
    paths = target
    state = load_state(paths)

    if assignee not in state.collaborator_ids():
        typer.echo(
            f"error: unknown assignee '{assignee}'. "
            f"Register with `cairn collaborator add` first.",
            err=True,
        )
        raise typer.Exit(code=1)

    id_index = state.id_index()
    bad_refs = [r for r in related if r not in id_index]
    if bad_refs:
        typer.echo(
            f"error: --related refers to unknown entity ids: {', '.join(bad_refs)}",
            err=True,
        )
        raise typer.Exit(code=1)

    parsed_due = _parse_due(due_date)
    new_id = next_id("A", state.action_ids())
    now = datetime.now(timezone.utc).replace(microsecond=0)

    try:
        new_action = ActionItem.model_validate(
            {
                "id": new_id,
                "assignee": assignee,
                "text": text,
                "created": now,
                "due_date": parsed_due,
                "status": "open",
                "related": related,
            }
        )
    except ValidationError as exc:
        typer.echo(f"error: schema validation failed:\n{exc}", err=True)
        raise typer.Exit(code=1) from None

    actions = [*state.actions, new_action]
    try:
        write_actions(paths, actions)
        repo = Repo(paths.root)
        commit(
            repo,
            [paths.action_items_yaml],
            message=f"{new_id}: {text[:60]}",
            author=get_user_identity(repo),
        )
    except CairnError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=1) from None

    typer.echo(f"Added {new_id}.")


@app.command(name="complete")
def complete(
    action_id: str = typer.Argument(..., help="Action ID, e.g. A-014."),
    by: str | None = typer.Option(
        None,
        "--by",
        help="Collaborator id of the completer. Defaults to the current --assignee.",
    ),
) -> None:
    """Mark an action item complete; status, completed_at, and completed_by are recorded."""
    target = resolve_target()

    # --- Remote-MCP dispatch (US-P-13) ---------------------------------------
    if isinstance(target, RemoteTarget):
        _complete_remote(target, action_id=action_id, by=by)
        return

    # --- Local dispatch ------------------------------------------------------
    paths = target
    state = load_state(paths)

    item = next((a for a in state.actions if a.id == action_id), None)
    if item is None:
        typer.echo(f"error: no action item with id '{action_id}'", err=True)
        raise typer.Exit(code=1)
    if item.status == "complete":
        typer.echo(f"error: {action_id} is already complete (no-op)", err=True)
        raise typer.Exit(code=1)

    completed_by = by or item.assignee
    if completed_by not in state.collaborator_ids():
        typer.echo(
            f"error: completer '{completed_by}' is not a known collaborator",
            err=True,
        )
        raise typer.Exit(code=1)

    now = datetime.now(timezone.utc).replace(microsecond=0)
    updated = item.model_copy(
        update={"status": "complete", "completed_at": now, "completed_by": completed_by}
    )
    actions = [updated if a.id == action_id else a for a in state.actions]

    try:
        write_actions(paths, actions)
        repo = Repo(paths.root)
        commit(
            repo,
            [paths.action_items_yaml],
            message=f"Complete {action_id}",
            author=get_user_identity(repo),
        )
    except CairnError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=1) from None

    typer.echo(f"Completed {action_id}.")


def _add_remote(
    target: RemoteTarget,
    *,
    assignee: str,
    text: str,
    due_date: str | None,
    related: list[str],
) -> None:
    from ..credentials import missing_token_hint
    from ..mcp.remote import RemoteAuthError, RemoteCallError, RemoteNetworkError, call_tool

    if target.token is None:
        typer.echo(f"error: {missing_token_hint(target.endpoint)}", err=True)
        raise typer.Exit(code=1)

    args: dict = {
        "text": text,
        "assignee": assignee,
        "cairn": target.cairn_name,
    }
    if due_date:
        args["due_date"] = due_date
    if related:
        args["related"] = related

    try:
        result = call_tool(target.endpoint, "add_action", args, token=target.token)
    except RemoteAuthError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=1) from None
    except RemoteNetworkError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=1) from None
    except RemoteCallError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=1) from None

    resolved_cairn = result.get("cairn", target.cairn_name)
    new_id = result.get("id", "?")
    typer.echo(f"Added {new_id} in cairn '{resolved_cairn}' at {target.endpoint}.")


def _complete_remote(
    target: RemoteTarget,
    *,
    action_id: str,
    by: str | None,
) -> None:
    from ..credentials import missing_token_hint
    from ..mcp.remote import RemoteAuthError, RemoteCallError, RemoteNetworkError, call_tool

    if target.token is None:
        typer.echo(f"error: {missing_token_hint(target.endpoint)}", err=True)
        raise typer.Exit(code=1)

    args: dict = {
        "id": action_id,
        "cairn": target.cairn_name,
    }
    if by:
        args["by"] = by

    try:
        result = call_tool(target.endpoint, "complete_action", args, token=target.token)
    except RemoteAuthError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=1) from None
    except RemoteNetworkError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=1) from None
    except RemoteCallError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=1) from None

    resolved_cairn = result.get("cairn", target.cairn_name)
    completed_id = result.get("id", action_id)
    typer.echo(
        f"Completed {completed_id} in cairn '{resolved_cairn}' at {target.endpoint}."
    )
