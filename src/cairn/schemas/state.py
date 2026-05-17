"""Aggregate state model for a cairn — all five files together."""

from __future__ import annotations

from dataclasses import dataclass, field

from .actions import ActionItem
from .collaborators import Collaborator
from .decisions import Decision
from .goals import Goal
from .questions import OpenQuestion

KIND_BY_PREFIX = {"D": "decision", "Q": "question", "A": "action", "G": "goal"}


@dataclass
class CairnState:
    """In-memory view of a cairn's five canonical state files."""

    collaborators: list[Collaborator] = field(default_factory=list)
    decisions: list[Decision] = field(default_factory=list)
    questions: list[OpenQuestion] = field(default_factory=list)
    actions: list[ActionItem] = field(default_factory=list)
    goals: list[Goal] = field(default_factory=list)

    def collaborator_ids(self) -> set[str]:
        return {c.id for c in self.collaborators}

    def id_index(self) -> dict[str, str]:
        """Return ``{entity_id: kind}`` over decisions, questions, actions, goals."""
        index: dict[str, str] = {}
        for d in self.decisions:
            index[d.id] = "decision"
        for q in self.questions:
            index[q.id] = "question"
        for a in self.actions:
            index[a.id] = "action"
        for g in self.goals:
            index[g.id] = "goal"
        return index

    def decision_ids(self) -> list[str]:
        return [d.id for d in self.decisions]

    def question_ids(self) -> list[str]:
        return [q.id for q in self.questions]

    def action_ids(self) -> list[str]:
        return [a.id for a in self.actions]

    def goal_ids(self) -> list[str]:
        return [g.id for g in self.goals]
