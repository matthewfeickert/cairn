"""Entity ID utilities: parsing, generation."""

from __future__ import annotations

import re
from typing import Final

ID_PATTERN: Final = re.compile(r"^(?P<kind>[A-Z])-(?P<num>\d{3,})$")

KIND_PREFIXES: Final[dict[str, str]] = {
    "decision": "D",
    "question": "Q",
    "action": "A",
    "goal": "G",
}


def parse_id(value: str) -> tuple[str, int]:
    """Return (kind_prefix, number) for an ID like ``D-014``."""
    match = ID_PATTERN.match(value)
    if not match:
        raise ValueError(f"not a valid Cairn ID: {value!r}")
    return match.group("kind"), int(match.group("num"))


def next_id(prefix: str, existing: list[str]) -> str:
    """Return the next available ID with the given single-letter ``prefix``.

    Numbers are zero-padded to three digits, growing as needed (D-001 ... D-1042).
    Gaps are not reused — the next ID is always one greater than the current max.
    """
    if len(prefix) != 1 or not prefix.isalpha() or not prefix.isupper():
        raise ValueError(f"prefix must be a single uppercase letter, got {prefix!r}")
    max_n = 0
    for value in existing:
        try:
            kind, num = parse_id(value)
        except ValueError:
            continue
        if kind == prefix and num > max_n:
            max_n = num
    return f"{prefix}-{max_n + 1:03d}"
