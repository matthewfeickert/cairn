"""YAML load / dump helpers.

Reads go through pyyaml (fast, simple). Writes go through ruamel.yaml so
that comments and key ordering humans have added by hand survive round
trips. The state files are intended to be human-editable; preserving
their incidental structure matters.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import yaml
from ruamel.yaml import YAML

_writer = YAML()
_writer.preserve_quotes = True
_writer.indent(mapping=2, sequence=4, offset=2)
_writer.width = 100


def load_yaml(path: Path) -> list[dict[str, Any]]:
    """Load a YAML file expected to contain a top-level list.

    An empty file or a file containing only ``[]`` returns an empty list.
    Returns the empty list (rather than ``None``) for compatibility with
    the schema-load helpers.
    """
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if data is None:
        return []
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected top-level YAML list, got {type(data).__name__}")
    return data


def dump_yaml(path: Path, items: list[dict[str, Any]]) -> None:
    """Write ``items`` to ``path`` as a YAML list.

    Atomic: writes to a sibling temp file and renames into place.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    if items:
        _writer.dump(items, buf)
    else:
        buf.write("[]\n")
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(buf.getvalue(), encoding="utf-8")
    tmp.replace(path)
