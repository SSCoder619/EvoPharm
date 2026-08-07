"""
Scoring utilities for the EvoPharm Architecture Analyzer.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Score:

    name: str

    earned: int

    maximum: int

    @property
    def percentage(self) -> float:
        if self.maximum == 0:
            return 100.0
        return round((self.earned / self.maximum) * 100, 2)


class ScoreCard:

    def __init__(self) -> None:
        self._scores: list[Score] = []

    def add(self, name: str, earned: int, maximum: int) -> None:
        self._scores.append(
            Score(
                name=name,
                earned=earned,
                maximum=maximum,
            )
        )

    @property
    def scores(self) -> list[Score]:
        return self._scores

    @property
    def overall(self) -> float:

        earned = sum(score.earned for score in self._scores)

        maximum = sum(score.maximum for score in self._scores)

        if maximum == 0:
            return 100.0

        return round((earned / maximum) * 100, 2)