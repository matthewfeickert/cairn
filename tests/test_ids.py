"""Tests for cairn.ids."""

from __future__ import annotations

import pytest

from cairn.ids import next_id, parse_id


def test_parse_id_extracts_kind_and_number():
    assert parse_id("D-014") == ("D", 14)
    assert parse_id("Q-007") == ("Q", 7)
    assert parse_id("A-1042") == ("A", 1042)


def test_parse_id_rejects_invalid():
    with pytest.raises(ValueError):
        parse_id("d-001")
    with pytest.raises(ValueError):
        parse_id("D-1")
    with pytest.raises(ValueError):
        parse_id("X")


def test_next_id_starts_at_001():
    assert next_id("D", []) == "D-001"


def test_next_id_increments_from_max():
    assert next_id("D", ["D-001", "D-014", "D-002"]) == "D-015"


def test_next_id_ignores_other_kinds():
    assert next_id("D", ["Q-099", "A-500"]) == "D-001"


def test_next_id_grows_beyond_three_digits():
    assert next_id("D", ["D-999"]) == "D-1000"


def test_next_id_rejects_bad_prefix():
    with pytest.raises(ValueError):
        next_id("DD", [])
    with pytest.raises(ValueError):
        next_id("d", [])
