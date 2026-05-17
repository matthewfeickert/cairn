"""Exception hierarchy for Cairn."""

from __future__ import annotations


class CairnError(Exception):
    """Base class for all Cairn errors."""


class SchemaError(CairnError):
    """A state file failed schema validation."""


class RefError(CairnError):
    """A cross-reference points to a non-existent entity."""


class CollisionError(CairnError):
    """An entity ID is already in use."""


class NotACairnError(CairnError):
    """The current working directory is not inside a cairn."""


class NoUserIdentityError(CairnError):
    """Git user.name / user.email is not configured."""
