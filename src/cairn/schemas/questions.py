"""Open question schema."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from .common import CollaboratorId, EntityId, UtcDatetime

QuestionId = Annotated[str, StringConstraints(pattern=r"^Q-\d{3,}$")]


class OpenQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: QuestionId
    raised_by: CollaboratorId
    date: UtcDatetime
    question: str = Field(min_length=1)
    status: Literal["open", "answered", "closed"] = "open"
    answered_by: EntityId | None = None
    related: list[EntityId] = Field(default_factory=list)
