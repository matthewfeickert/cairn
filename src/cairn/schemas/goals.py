"""Goal schema."""

from __future__ import annotations

from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from .common import EntityId, UtcDatetime

GoalId = Annotated[str, StringConstraints(pattern=r"^G-\d{3,}$")]


class Goal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: GoalId
    text: str = Field(min_length=1)
    target_date: date | None = None
    status: Literal["active", "achieved", "abandoned"] = "active"
    created: UtcDatetime
    related: list[EntityId] = Field(default_factory=list)
