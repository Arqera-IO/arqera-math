"""Decision Theory Service.

Provides multi-criteria decision analysis:
- Weighted multi-criteria decision matrix with normalization
- Score ranking and sensitivity analysis
- Convenience functions for quick decision scoring

Standalone — no SQLAlchemy or external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


@dataclass
class DecisionCriterion:
    """A single criterion in a decision matrix."""

    name: str
    weight: float  # 0.0 to 1.0
    minimize: bool = False  # True = lower is better


@dataclass
class DecisionOption:
    """An option to evaluate across criteria."""

    name: str
    scores: dict[str, float] = field(default_factory=dict)  # criterion_name -> score


@dataclass
class DecisionResult:
    """Result for a single option after evaluation."""

    result_id: str = field(default_factory=lambda: str(uuid4()))
    option_name: str = ""
    weighted_score: float = 0.0
    criterion_scores: dict[str, float] = field(default_factory=dict)
    rank: int = 0
    measured_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "option_name": self.option_name,
            "weighted_score": self.weighted_score,
            "criterion_scores": dict(self.criterion_scores),
            "rank": self.rank,
            "measured_at": self.measured_at.isoformat(),
        }


class DecisionMatrix:
    """Weighted multi-criteria decision matrix.

    Normalizes scores 0-1 per criterion, applies weights,
    handles minimize/maximize directions, and ranks options.
    """

    def evaluate(
        self,
        criteria: list[DecisionCriterion],
        options: list[DecisionOption],
    ) -> list[DecisionResult]:
        """Score and rank all options.

        Normalizes scores 0-1 per criterion, applies weights,
        handles minimize/maximize.

        Args:
            criteria: List of criteria with weights and directions.
            options: List of options with raw scores per criterion.

        Returns:
            List of DecisionResult sorted by rank (1 = best).
        """
        if not criteria or not options:
            return []

        # Collect min/max per criterion for normalization
        criterion_names = [c.name for c in criteria]
        raw: dict[str, list[float]] = {name: [] for name in criterion_names}
        for option in options:
            for name in criterion_names:
                raw[name].append(option.scores.get(name, 0.0))

        mins = {name: min(vals) if vals else 0.0 for name, vals in raw.items()}
        maxs = {name: max(vals) if vals else 0.0 for name, vals in raw.items()}

        # Build results
        now = datetime.now(UTC)
        results: list[DecisionResult] = []

        for option in options:
            criterion_scores: dict[str, float] = {}
            total = 0.0

            for criterion in criteria:
                name = criterion.name
                val = option.scores.get(name, 0.0)
                span = maxs[name] - mins[name]

                normalized = (val - mins[name]) / span if span > 0 else 1.0

                if criterion.minimize:
                    normalized = 1.0 - normalized

                weighted = normalized * criterion.weight
                criterion_scores[name] = weighted
                total += weighted

            results.append(DecisionResult(
                option_name=option.name,
                weighted_score=total,
                criterion_scores=criterion_scores,
                rank=0,
                measured_at=now,
            ))

        # Sort descending by score, assign ranks
        results.sort(key=lambda r: r.weighted_score, reverse=True)
        for i, result in enumerate(results):
            result.rank = i + 1

        return results

    def sensitivity_analysis(
        self,
        criteria: list[DecisionCriterion],
        options: list[DecisionOption],
        vary_criterion: str,
        steps: int = 5,
    ) -> dict[str, Any]:
        """Vary one criterion's weight and show how rankings change.

        Varies the named criterion's weight from 0.0 to 1.0 in equal steps.
        Other weights are scaled proportionally to fill the remainder.

        Args:
            criteria: List of criteria definitions.
            options: List of options to evaluate.
            vary_criterion: Name of the criterion to vary.
            steps: Number of weight steps from 0.0 to 1.0.

        Returns:
            Dict with 'vary_criterion', 'weights' (list of tested weights),
            and 'rankings' (dict mapping option name to list of ranks).
        """
        if steps < 2:
            steps = 2

        test_weights = [i / (steps - 1) for i in range(steps)]
        rankings: dict[str, list[int]] = {opt.name: [] for opt in options}

        for test_weight in test_weights:
            remaining = 1.0 - test_weight
            other_total = sum(
                c.weight for c in criteria if c.name != vary_criterion
            )

            modified: list[DecisionCriterion] = []
            for c in criteria:
                if c.name == vary_criterion:
                    modified.append(DecisionCriterion(
                        name=c.name,
                        weight=test_weight,
                        minimize=c.minimize,
                    ))
                else:
                    scaled = (
                        (c.weight / other_total * remaining)
                        if other_total > 0 else 0.0
                    )
                    modified.append(DecisionCriterion(
                        name=c.name,
                        weight=scaled,
                        minimize=c.minimize,
                    ))

            results = self.evaluate(modified, options)
            for r in results:
                rankings[r.option_name].append(r.rank)

        return {
            "vary_criterion": vary_criterion,
            "weights": test_weights,
            "rankings": rankings,
        }


def decision_rank(
    criteria: list[dict[str, Any]],
    options: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Convenience function for quick decision ranking.

    Args:
        criteria: List of dicts with keys: name, weight, minimize (optional).
        options: List of dicts with keys: name, scores (dict).

    Returns:
        List of result dicts sorted by rank.
    """
    parsed_criteria = [
        DecisionCriterion(
            name=c["name"],
            weight=c["weight"],
            minimize=c.get("minimize", False),
        )
        for c in criteria
    ]
    parsed_options = [
        DecisionOption(name=o["name"], scores=o["scores"])
        for o in options
    ]

    matrix = DecisionMatrix()
    results = matrix.evaluate(parsed_criteria, parsed_options)
    return [r.to_dict() for r in results]


def weighted_score(
    scores: dict[str, float],
    weights: dict[str, float],
) -> float:
    """Simple weighted sum.

    Returns sum(score * weight) for each key present in scores.

    Args:
        scores: Score values keyed by criterion name.
        weights: Weight values keyed by criterion name.

    Returns:
        Weighted sum as float.
    """
    return sum(
        scores.get(k, 0.0) * weights.get(k, 0.0)
        for k in scores
    )
