"""Section-aware reader/writer for the cairn's PROJECT.md.

PROJECT.md is structured as a sequence of H2 sections under an H1 title.
This module exposes get/set per section so callers (MCP tools, CLI
commands) can address sections by name without touching the file's
exact byte layout. Section names match exact H2 heading text.

This is a deliberate semantic API over the storage layout. A future
refactor may split PROJECT.md into multiple files (state/overview.md,
state/current_focus.yaml, ...) without changing this module's signature.
See ADR-0009 §⚠️19 in `docs/open-questions.md` for the longer story.
"""

from __future__ import annotations

import re

# The canonical section set the cairn knows about. Additional H2 sections
# users add by hand are preserved on round-trip but not addressable by name.
KNOWN_SECTIONS = ("Overview", "Current focus", "Related repositories")

_H2 = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def parse(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Split PROJECT.md into (preamble, [(section_name, content), ...]).

    The preamble is everything before the first H2 (typically the H1 title
    plus the italic agent-orientation tagline). Each section's content
    includes its body but **not** its `## Heading` line.
    """
    starts = [(m.start(), m.end(), m.group(1)) for m in _H2.finditer(text)]
    if not starts:
        return text, []
    preamble = text[: starts[0][0]]
    sections: list[tuple[str, str]] = []
    for i, (_, body_start, name) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
        sections.append((name, text[body_start:end]))
    return preamble, sections


def render(preamble: str, sections: list[tuple[str, str]]) -> str:
    """Reverse of parse — reassembles a full PROJECT.md from its parts."""
    out = preamble
    if not out.endswith("\n"):
        out += "\n"
    for name, content in sections:
        out += f"## {name}\n"
        if not content.startswith("\n"):
            out += "\n"
        out += content
        if not content.endswith("\n"):
            out += "\n"
    return out


def get_section(text: str, name: str) -> str | None:
    """Return the named section's content (without its heading), or None."""
    _, sections = parse(text)
    for section_name, content in sections:
        if section_name.strip().lower() == name.strip().lower():
            return content.strip("\n")
    return None


def set_section(text: str, name: str, content: str) -> str:
    """Replace the named section's content. Adds the section if missing.

    The new content is inserted in the canonical position when added: if the
    section is one of KNOWN_SECTIONS, it goes in that order relative to other
    known sections; otherwise it's appended at the end.

    The supplied content should be the section body only — no leading
    `## Heading` line.
    """
    preamble, sections = parse(text)
    existing = {n.strip().lower(): i for i, (n, _) in enumerate(sections)}
    canonical = name.strip()
    norm = canonical.lower()

    body = content.strip("\n") + "\n"

    if norm in existing:
        sections[existing[norm]] = (sections[existing[norm]][0], body)
    else:
        # Insert at the canonical position for known sections; otherwise append.
        if canonical in KNOWN_SECTIONS:
            order = list(KNOWN_SECTIONS)
            target_rank = order.index(canonical)
            existing_ranks = []
            for i, (n, _) in enumerate(sections):
                if n in order:
                    existing_ranks.append((order.index(n), i))
            existing_ranks.sort()
            insertion = len(sections)
            for rank, idx in existing_ranks:
                if rank > target_rank:
                    insertion = idx
                    break
            sections.insert(insertion, (canonical, body))
        else:
            sections.append((canonical, body))

    return render(preamble, sections)
