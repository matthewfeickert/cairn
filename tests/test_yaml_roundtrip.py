"""YAML I/O round-trip tests for state files."""

from __future__ import annotations

from pathlib import Path

from cairn.io.state_io import (
    load_collaborators,
    load_decisions,
    write_collaborators,
    write_decisions,
)
from cairn.io.yaml_io import dump_yaml, load_yaml
from cairn.paths import CairnPaths
from cairn.schemas import Collaborator, Decision


def _make_cairn(tmp_path: Path) -> CairnPaths:
    paths = CairnPaths(root=tmp_path)
    paths.state.mkdir(parents=True)
    for name in ("decisions", "open_questions", "action_items", "goals", "collaborators"):
        (paths.state / f"{name}.yaml").write_text("[]\n", encoding="utf-8")
    return paths


def test_empty_yaml_loads_as_empty_list(tmp_path: Path):
    p = tmp_path / "x.yaml"
    p.write_text("[]\n")
    assert load_yaml(p) == []


def test_missing_file_loads_as_empty_list(tmp_path: Path):
    assert load_yaml(tmp_path / "missing.yaml") == []


def test_dump_empty_writes_bracket_pair(tmp_path: Path):
    p = tmp_path / "x.yaml"
    dump_yaml(p, [])
    assert p.read_text() == "[]\n"


def test_collaborator_roundtrip(tmp_path: Path):
    paths = _make_cairn(tmp_path)
    c = Collaborator(
        id="maria",
        name="Maria Santos",
        role="postdoc",
        expertise=["causal inference"],
    )
    write_collaborators(paths, [c])
    loaded = load_collaborators(paths)
    assert len(loaded) == 1
    assert loaded[0].id == "maria"
    assert loaded[0].expertise == ["causal inference"]


def test_decision_roundtrip(tmp_path: Path):
    paths = _make_cairn(tmp_path)
    d = Decision(
        id="D-001",
        date="2026-05-17T10:00:00Z",
        author="kyle",
        decision="Use stratified resampling",
        related=["Q-007"],
    )
    write_decisions(paths, [d])
    text = paths.decisions_yaml.read_text()
    assert "D-001" in text
    assert "2026-05-17T10:00:00Z" in text
    loaded = load_decisions(paths)
    assert loaded[0].decision == "Use stratified resampling"
    assert loaded[0].related == ["Q-007"]
