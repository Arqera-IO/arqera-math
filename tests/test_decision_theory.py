"""Tests for Decision Theory Service."""

from arqera_math import (
    DecisionCriterion,
    DecisionMatrix,
    DecisionOption,
    DecisionResult,
    decision_rank,
    weighted_score,
)


def test_evaluate_three_options():
    """DecisionMatrix.evaluate ranks options correctly with normalization."""
    criteria = [
        DecisionCriterion(name="cost", weight=0.3, minimize=True),
        DecisionCriterion(name="quality", weight=0.5),
        DecisionCriterion(name="speed", weight=0.2),
    ]
    options = [
        DecisionOption(name="A", scores={"cost": 8, "quality": 6, "speed": 7}),
        DecisionOption(name="B", scores={"cost": 5, "quality": 9, "speed": 6}),
        DecisionOption(name="C", scores={"cost": 7, "quality": 7, "speed": 8}),
    ]

    matrix = DecisionMatrix()
    results = matrix.evaluate(criteria, options)

    assert len(results) == 3
    assert all(isinstance(r, DecisionResult) for r in results)
    # Ranks must be 1, 2, 3
    assert [r.rank for r in results] == [1, 2, 3]
    # Scores must be descending
    scores = [r.weighted_score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_evaluate_minimize_criterion():
    """Minimize criteria should favor lower raw scores."""
    criteria = [
        DecisionCriterion(name="cost", weight=1.0, minimize=True),
    ]
    options = [
        DecisionOption(name="cheap", scores={"cost": 10}),
        DecisionOption(name="expensive", scores={"cost": 100}),
    ]

    matrix = DecisionMatrix()
    results = matrix.evaluate(criteria, options)

    # Cheap should rank first (lower cost is better with minimize=True)
    assert results[0].option_name == "cheap"
    assert results[0].rank == 1
    assert results[1].option_name == "expensive"
    assert results[1].rank == 2


def test_evaluate_empty_inputs():
    """evaluate returns empty list for empty criteria or options."""
    matrix = DecisionMatrix()
    assert matrix.evaluate([], []) == []
    assert matrix.evaluate(
        [DecisionCriterion(name="x", weight=1.0)], []
    ) == []
    assert matrix.evaluate(
        [], [DecisionOption(name="A", scores={"x": 1})]
    ) == []


def test_sensitivity_analysis_structure():
    """sensitivity_analysis returns correct structure."""
    criteria = [
        DecisionCriterion(name="speed", weight=0.5),
        DecisionCriterion(name="cost", weight=0.5, minimize=True),
    ]
    options = [
        DecisionOption(name="A", scores={"speed": 9, "cost": 3}),
        DecisionOption(name="B", scores={"speed": 5, "cost": 8}),
    ]

    matrix = DecisionMatrix()
    result = matrix.sensitivity_analysis(criteria, options, "speed", steps=5)

    assert result["vary_criterion"] == "speed"
    assert len(result["weights"]) == 5
    assert "A" in result["rankings"]
    assert "B" in result["rankings"]
    assert len(result["rankings"]["A"]) == 5
    assert len(result["rankings"]["B"]) == 5
    # Weights should range from 0.0 to 1.0
    assert abs(result["weights"][0] - 0.0) < 1e-6
    assert abs(result["weights"][-1] - 1.0) < 1e-6


def test_sensitivity_analysis_ranking_shifts():
    """Rankings should shift when weight is varied from 0 to 1."""
    criteria = [
        DecisionCriterion(name="speed", weight=0.5),
        DecisionCriterion(name="cost", weight=0.5),
    ]
    options = [
        DecisionOption(name="fast", scores={"speed": 10, "cost": 2}),
        DecisionOption(name="cheap", scores={"speed": 2, "cost": 10}),
    ]

    matrix = DecisionMatrix()
    result = matrix.sensitivity_analysis(criteria, options, "speed", steps=3)

    # At weight=0 for speed (only cost matters), "cheap" should rank 1
    assert result["rankings"]["cheap"][0] == 1
    # At weight=1 for speed (only speed matters), "fast" should rank 1
    assert result["rankings"]["fast"][-1] == 1


def test_decision_rank_convenience():
    """decision_rank convenience function returns sorted dicts."""
    criteria = [
        {"name": "reliability", "weight": 0.6},
        {"name": "latency", "weight": 0.4, "minimize": True},
    ]
    options = [
        {"name": "server-A", "scores": {"reliability": 0.9, "latency": 0.2}},
        {"name": "server-B", "scores": {"reliability": 0.7, "latency": 0.8}},
    ]

    results = decision_rank(criteria, options)

    assert len(results) == 2
    assert isinstance(results[0], dict)
    assert results[0]["rank"] == 1
    assert results[1]["rank"] == 2
    # server-A has higher reliability and lower latency, should rank first
    assert results[0]["option_name"] == "server-A"


def test_weighted_score_simple():
    """weighted_score computes sum of score*weight pairs."""
    scores = {"speed": 0.9, "cost": 0.6, "reliability": 0.8}
    weights = {"speed": 0.4, "cost": 0.3, "reliability": 0.3}

    result = weighted_score(scores, weights)
    # 0.9*0.4 + 0.6*0.3 + 0.8*0.3 = 0.36 + 0.18 + 0.24 = 0.78
    assert abs(result - 0.78) < 1e-6


def test_decision_result_to_dict():
    """DecisionResult.to_dict serializes all fields."""
    result = DecisionResult(
        option_name="test",
        weighted_score=0.85,
        criterion_scores={"x": 0.5},
        rank=1,
    )
    d = result.to_dict()
    assert d["option_name"] == "test"
    assert d["weighted_score"] == 0.85
    assert d["rank"] == 1
    assert "result_id" in d
    assert "measured_at" in d
