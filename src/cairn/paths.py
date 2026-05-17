"""Path resolution for a cairn on disk."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .errors import NotACairnError

STATE_FILES = (
    "decisions.yaml",
    "open_questions.yaml",
    "action_items.yaml",
    "goals.yaml",
    "collaborators.yaml",
)

REQUIRED_DIRS = (
    "state",
    "knowledge",
    "knowledge/meetings",
    "knowledge/findings",
    "knowledge/literature",
    "knowledge/provenance",
    "skills",
    "branches",
)


@dataclass(frozen=True)
class CairnPaths:
    """Resolved paths inside a cairn."""

    root: Path

    @property
    def state(self) -> Path:
        return self.root / "state"

    @property
    def knowledge(self) -> Path:
        return self.root / "knowledge"

    @property
    def meetings(self) -> Path:
        return self.knowledge / "meetings"

    @property
    def findings(self) -> Path:
        return self.knowledge / "findings"

    @property
    def literature(self) -> Path:
        return self.knowledge / "literature"

    @property
    def provenance(self) -> Path:
        return self.knowledge / "provenance"

    @property
    def skills(self) -> Path:
        return self.root / "skills"

    @property
    def branches(self) -> Path:
        return self.root / "branches"

    @property
    def project_md(self) -> Path:
        return self.root / "PROJECT.md"

    @property
    def collaborators_yaml(self) -> Path:
        return self.state / "collaborators.yaml"

    @property
    def decisions_yaml(self) -> Path:
        return self.state / "decisions.yaml"

    @property
    def open_questions_yaml(self) -> Path:
        return self.state / "open_questions.yaml"

    @property
    def action_items_yaml(self) -> Path:
        return self.state / "action_items.yaml"

    @property
    def goals_yaml(self) -> Path:
        return self.state / "goals.yaml"


def is_cairn_root(path: Path) -> bool:
    """A directory is a cairn root if it has ``state/collaborators.yaml``."""
    return (path / "state" / "collaborators.yaml").is_file()


def find_cairn_root(start: Path) -> Path:
    """Walk upward from ``start`` looking for a cairn root."""
    start = start.resolve()
    for candidate in (start, *start.parents):
        if is_cairn_root(candidate):
            return candidate
    raise NotACairnError(f"no cairn found at or above {start}")


def resolve_cairn(start: Path | None = None) -> CairnPaths:
    """Resolve the cairn containing ``start`` (defaults to cwd)."""
    return CairnPaths(root=find_cairn_root(start or Path.cwd()))
