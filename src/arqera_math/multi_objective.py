"""Multi-Objective Optimization Service.

Provides multi-objective analysis and Pareto optimization:
- Pareto frontier computation with dominance counting
- Dominance testing between points
- Weighted sum scalarization with direction handling

Standalone — no SQLAlchemy or external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


@dataclass
class ObjectiveWeight:
    """An objective with weight and optimization direction."""

    name: str
    weight: float  # 0.0 to 1.0
    minimize: bool = False


@dataclass
class ParetoPoint:
    """A single point in objective space with Pareto classification."""

    point_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    objectives: dict[str, float] = field(default_factory=dict)
    is_pareto_optimal: bool = False
    dominance_count: int = 0  # how many points this dominates

    def to_dict(self) -> dict[str, Any]:
        return {
            "point_id": self.point_id,
            "name": self.name,
            "objectives": dict(self.objectives),
            "is_pareto_optimal": self.is_pareto_optimal,
            "dominance_count": self.dominance_count,
        }


@dataclass
class ParetoResult:
    """Result of Pareto frontier computation."""

    result_id: str = field(default_factory=lambda: str(uuid4()))
    frontier: list[ParetoPoint] = field(default_factory=list)
    dominated: list[ParetoPoint] = field(default_factory=list)
    total_points: int = 0
    measured_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "frontier": [p.to_dict() for p in self.frontier],
            "dominated": [p.to_dict() for p in self.dominated],
            "total_points": self.total_points,
            "measured_at": self.measured_at.isoformat(),
        }


def pareto_frontier(
    points: list[dict[str, Any]],
    minimize: set[str] | None = None,
) -> ParetoResult:
    """Compute Pareto frontier.

    A point is Pareto-optimal if no other point is better or equal in ALL
    objectives and strictly better in at least one.

    Args:
        points: List of dicts with keys 'name' and 'objectives' (dict of values).
        minimize: Set of objective names to minimize (default: maximize all).

    Returns:
        ParetoResult with frontier and dominated points.
    """
    if minimize is None:
        minimize = set()

    n = len(points)
    pareto_points: list[ParetoPoint] = []

    for i, p in enumerate(points):
        obj_i = p.get("objectives", {})
        name_i = p.get("name", f"point_{i}")

        # Count how many other points this one dominates
        dom_count = 0
        for j, q in enumerate(points):
            if i == j:
                continue
            obj_j = q.get("objectives", {})
            if dominates(obj_i, obj_j, minimize):
                dom_count += 1

        pareto_points.append(ParetoPoint(
            name=name_i,
            objectives=dict(obj_i),
            is_pareto_optimal=False,
            dominance_count=dom_count,
        ))

    # Determine Pareto optimality: not dominated by any other point
    for i, pp in enumerate(pareto_points):
        is_dominated = False
        for j, other in enumerate(pareto_points):
            if i == j:
                continue
            if dominates(other.objectives, pp.objectives, minimize):
                is_dominated = True
                break
        pp.is_pareto_optimal = not is_dominated

    frontier = [p for p in pareto_points if p.is_pareto_optimal]
    dominated_list = [p for p in pareto_points if not p.is_pareto_optimal]

    return ParetoResult(
        frontier=frontier,
        dominated=dominated_list,
        total_points=n,
    )


def weighted_sum(
    objectives: dict[str, float],
    weights: list[ObjectiveWeight],
) -> float:
    """Weighted sum scalarization for multi-objective optimization.

    Handles minimize by negating the score before weighting.

    Args:
        objectives: Objective values keyed by name.
        weights: List of ObjectiveWeight definitions.

    Returns:
        Weighted sum score (higher is always better).
    """
    total = 0.0
    for w in weights:
        val = objectives.get(w.name, 0.0)
        if w.minimize:
            val = -val
        total += val * w.weight
    return total


def dominates(
    a: dict[str, float],
    b: dict[str, float],
    minimize: set[str] | None = None,
) -> bool:
    """Check if point a dominates point b.

    Returns True if a is at least as good as b on all objectives
    and strictly better on at least one.

    Args:
        a: Objective values for point a.
        b: Objective values for point b.
        minimize: Set of objective names to minimize (default: maximize all).

    Returns:
        True if a dominates b.
    """
    if minimize is None:
        minimize = set()

    all_keys = set(a.keys()) | set(b.keys())
    if not all_keys:
        return False

    at_least_as_good = True
    strictly_better = False

    for key in all_keys:
        val_a = a.get(key, 0.0)
        val_b = b.get(key, 0.0)

        if key in minimize:
            # Lower is better
            if val_a > val_b:
                at_least_as_good = False
                break
            if val_a < val_b:
                strictly_better = True
        else:
            # Higher is better
            if val_a < val_b:
                at_least_as_good = False
                break
            if val_a > val_b:
                strictly_better = True

    return at_least_as_good and strictly_better
