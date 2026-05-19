"""Tests for the PROJECT.md section parser (project_md.py)."""

from __future__ import annotations

from cairn import project_md as pm

SAMPLE = """# test-project

*Agent orientation file.*

## Overview

Project X is about Y.
It is in stage Z.

## Current focus

- Item one
- Item two

## Related repositories

- repo-a — analysis
- repo-b — paper
"""


def test_parse_extracts_sections():
    preamble, sections = pm.parse(SAMPLE)
    assert "test-project" in preamble
    names = [n for n, _ in sections]
    assert names == ["Overview", "Current focus", "Related repositories"]


def test_get_section_returns_content_without_heading():
    out = pm.get_section(SAMPLE, "Overview")
    assert out is not None
    assert "Project X is about Y" in out
    assert "## Overview" not in out


def test_get_section_case_insensitive():
    out = pm.get_section(SAMPLE, "overview")
    assert out is not None and "Project X" in out


def test_get_section_returns_none_for_missing():
    assert pm.get_section(SAMPLE, "Nonexistent") is None


def test_set_section_replaces_existing():
    updated = pm.set_section(SAMPLE, "Overview", "Completely new overview.")
    assert "Completely new overview." in updated
    assert "Project X is about Y" not in updated
    # Other sections preserved
    assert "## Current focus" in updated
    assert "## Related repositories" in updated


def test_set_section_adds_known_section_in_canonical_position():
    # Remove "Current focus" from SAMPLE-like text, then re-add via set_section
    text = SAMPLE.replace(
        "## Current focus\n\n- Item one\n- Item two\n\n", ""
    )
    updated = pm.set_section(text, "Current focus", "- new item\n")
    # Should appear between Overview and Related repositories
    overview_idx = updated.find("## Overview")
    focus_idx = updated.find("## Current focus")
    repos_idx = updated.find("## Related repositories")
    assert 0 < overview_idx < focus_idx < repos_idx


def test_set_section_appends_unknown_section_at_end():
    updated = pm.set_section(SAMPLE, "Random extra", "body")
    sections = [n for n, _ in pm.parse(updated)[1]]
    assert sections[-1] == "Random extra"


def test_round_trip_preserves_known_sections():
    preamble, sections = pm.parse(SAMPLE)
    rendered = pm.render(preamble, sections)
    # Section names + content should match
    _, s2 = pm.parse(rendered)
    assert [n for n, _ in s2] == [n for n, _ in sections]


def test_set_section_creates_first_section_in_empty_doc():
    text = "# my-project\n\n"
    updated = pm.set_section(text, "Overview", "Hello.")
    assert "## Overview" in updated
    assert "Hello." in updated
