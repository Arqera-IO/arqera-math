"""Tests for Multi-Objective Optimization Service."""

from arqera_math import (
    ObjectiveWeight,
    ParetoPoint,
    ParetoResult,
    dominates,
    pareto_frontier,
    weighted_sum,
)


def test_pareto_frontier_basic():
    """Pareto frontier identifies optimal and dominated points."""
    points = [
        {"name": "A", "objectives": {"speed": 10, "cost": 5}},
        {"name": "B", "objectives": {"speed": 8, "cost": 3}},
        {"name": "C", "objectives": {"speed": 7, "cost": 6}},  # Dominated by A
    ]
    result = pareto_frontier(points, minimize={"cost"})

    assert isinstance(result, ParetoResult)
    assert result.total_points == 3
    assert len(result.frontier) == 2  # A and B are Pareto-optimal
    assert len(result.dominated) == 1  # C is dominated

    frontier_names = {p.name for p in result.frontier}
    assert "A" in frontier_names
    assert "B" in frontier_names

    dominated_names = {p.name for p in result.dominated}
    assert "C" in dominated_names


def test_pareto_frontier_all_optimal():
    """When all points trade off, all should be Pareto-optimal."""
    points = [
        {"name": "P1", "objectives": {"x": 1, "y": 3}},
        {"name": "P2", "objectives": {"x": 2, "y": 2}},
        {"name": "P3", "objectives": {"x": 3, "y": 1}},
    ]
    # Maximize both: each is best on one axis
    result = pareto_frontier(points)

    assert len(result.frontier) == 3
    assert len(result.dominated) == 0


def test_pareto_frontier_dominance_count():
    """Dominance count reflects how many points each dominates."""
    points = [
        {"name": "best", "objectives": {"x": 10, "y": 10}},  # Dominates all
        {"name": "mid", "objectives": {"x": 5, "y": 5}},
        {"name": "worst", "objectives": {"x": 1, "y": 1}},
    ]
    result = pareto_frontier(points)

    best = next(p for p in result.frontier if p.name == "best")
    assert best.dominance_count == 2
    assert best.is_pareto_optimal is True


def test_dominates_maximize():
    """dominates returns True when A >= B on all and > on at least one."""
    a = {"x": 10, "y": 5}
    b = {"x": 8, "y": 5}
    assert dominates(a, b) is True
    assert dominates(b, a) is False


def test_dominates_minimize():
    """dominates handles minimize objectives correctly."""
    a = {"cost": 3, "time": 2}
    b = {"cost": 5, "time": 4}
    assert dominates(a, b, minimize={"cost", "time"}) is True
    assert dominates(b, a, minimize={"cost", "time"}) is False


def test_dominates_tradeoff():
    """Neither dominates when there's a tradeoff."""
    a = {"x": 10, "y": 2}
    b = {"x": 5, "y": 8}
    assert dominates(a, b) is False
    assert dominates(b, a) is False


def test_weighted_sum_maximize():
    """weighted_sum sums values * weights for maximize objectives."""
    weights = [
        ObjectiveWeight(name="a", weight=0.3),
        ObjectiveWeight(name="b", weight=0.7),
    ]
    values = {"a": 10.0, "b": 5.0}
    score = weighted_sum(values, weights)
    # 10*0.3 + 5*0.7 = 3.0 + 3.5 = 6.5
    assert abs(score - 6.5) < 1e-6


def test_weighted_sum_with_minimize():
    """weighted_sum negates minimize objectives."""
    weights = [
        ObjectiveWeight(name="perf", weight=0.5),
        ObjectiveWeight(name="cost", weight=0.5, minimize=True),
    ]
    values = {"perf": 10.0, "cost": 4.0}
    score = weighted_sum(values, weights)
    # 10*0.5 + (-4)*0.5 = 5.0 - 2.0 = 3.0
    assert abs(score - 3.0) < 1e-6


def test_pareto_point_to_dict():
    """ParetoPoint.to_dict serializes all fields."""
    point = ParetoPoint(
        name="test",
        objectives={"x": 1.0, "y": 2.0},
        is_pareto_optimal=True,
        dominance_count=3,
    )
    d = point.to_dict()
    assert d["name"] == "test"
    assert d["objectives"] == {"x": 1.0, "y": 2.0}
    assert d["is_pareto_optimal"] is True
    assert d["dominance_count"] == 3
    assert "point_id" in d


def test_pareto_result_to_dict():
    """ParetoResult.to_dict serializes frontier and dominated."""
    result = ParetoResult(
        frontier=[ParetoPoint(name="A", is_pareto_optimal=True)],
        dominated=[ParetoPoint(name="B", is_pareto_optimal=False)],
        total_points=2,
    )
    d = result.to_dict()
    assert d["total_points"] == 2
    assert len(d["frontier"]) == 1
    assert len(d["dominated"]) == 1
    assert "result_id" in d
