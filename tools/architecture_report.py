"""
Pretty console reporting.
"""

from __future__ import annotations

from metrics import ScoreCard


class ArchitectureReport:

    WIDTH = 70

    @classmethod
    def title(cls, title: str) -> None:

        print("=" * cls.WIDTH)

        print(title.center(cls.WIDTH))

        print("=" * cls.WIDTH)

    @classmethod
    def section(cls, title: str) -> None:

        print()

        print(title)

        print("-" * cls.WIDTH)

    @classmethod
    def item(cls, key: str, value: object) -> None:

        print(f"{key:<30}: {value}")

    @classmethod
    def score(cls, scores: ScoreCard) -> None:

        cls.section("Scores")

        for score in scores.scores:

            cls.item(
                score.name,
                f"{score.percentage:.1f}%",
            )

        print()

        cls.item(
            "Overall",
            f"{scores.overall:.1f}%",
        )