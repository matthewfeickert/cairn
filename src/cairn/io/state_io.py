"""Load and write the five canonical state files as schema objects."""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, TypeAdapter, ValidationError

from ..errors import SchemaError
from ..paths import CairnPaths
from ..schemas import (
    ActionItem,
    CairnState,
    Collaborator,
    Decision,
    Goal,
    OpenQuestion,
)
from .yaml_io import dump_yaml, load_yaml

M = TypeVar("M", bound=BaseModel)


def _load_list(path, model: type[M]) -> list[M]:
    raw = load_yaml(path)
    adapter = TypeAdapter(list[model])
    try:
        return adapter.validate_python(raw)
    except ValidationError as exc:
        raise SchemaError(f"{path}: {exc}") from exc


def _dump_list(path, items: list[BaseModel]) -> None:
    serialized: list[dict[str, Any]] = [m.model_dump(mode="json", exclude_none=True) for m in items]
    dump_yaml(path, serialized)


def load_collaborators(paths: CairnPaths) -> list[Collaborator]:
    return _load_list(paths.collaborators_yaml, Collaborator)


def load_decisions(paths: CairnPaths) -> list[Decision]:
    return _load_list(paths.decisions_yaml, Decision)


def load_questions(paths: CairnPaths) -> list[OpenQuestion]:
    return _load_list(paths.open_questions_yaml, OpenQuestion)


def load_actions(paths: CairnPaths) -> list[ActionItem]:
    return _load_list(paths.action_items_yaml, ActionItem)


def load_goals(paths: CairnPaths) -> list[Goal]:
    return _load_list(paths.goals_yaml, Goal)


def load_state(paths: CairnPaths) -> CairnState:
    return CairnState(
        collaborators=load_collaborators(paths),
        decisions=load_decisions(paths),
        questions=load_questions(paths),
        actions=load_actions(paths),
        goals=load_goals(paths),
    )


def write_collaborators(paths: CairnPaths, items: list[Collaborator]) -> None:
    _dump_list(paths.collaborators_yaml, items)


def write_decisions(paths: CairnPaths, items: list[Decision]) -> None:
    _dump_list(paths.decisions_yaml, items)


def write_questions(paths: CairnPaths, items: list[OpenQuestion]) -> None:
    _dump_list(paths.open_questions_yaml, items)


def write_actions(paths: CairnPaths, items: list[ActionItem]) -> None:
    _dump_list(paths.action_items_yaml, items)


def write_goals(paths: CairnPaths, items: list[Goal]) -> None:
    _dump_list(paths.goals_yaml, items)
