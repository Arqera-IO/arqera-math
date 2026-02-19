"""Tests for Quorum Sensing Service."""

from arqera_math import QuorumResponse, QuorumSensingService, hill_function


def test_hill_function_zero_signal():
    """hill_function(0, ...) = 0."""
    assert hill_function(0.0, threshold=0.5, coefficient=2.0) == 0.0


def test_hill_function_at_threshold():
    """hill_function(K, K, n) = 0.5 by definition."""
    result = hill_function(0.5, threshold=0.5, coefficient=2.0)
    assert abs(result - 0.5) < 1e-10


def test_hill_function_high_signal():
    """High signal approaches 1.0."""
    result = hill_function(10.0, threshold=0.5, coefficient=2.0)
    assert result > 0.99


def test_hill_function_coefficient_steepness():
    """Higher coefficient = steeper curve around threshold."""
    # At signal = 0.3 (below K=0.5), higher n should give lower response
    r_low_n = hill_function(0.3, threshold=0.5, coefficient=1.0)
    r_high_n = hill_function(0.3, threshold=0.5, coefficient=4.0)
    assert r_high_n < r_low_n


def test_quorum_activation():
    """Activated flag based on QUORUM_ACTIVATION_THRESHOLD (0.8)."""
    svc = QuorumSensingService()

    # Low signal — not activated
    low = svc.evaluate_signal(0.1, threshold=0.5, coefficient=2.0)
    assert not low.activated

    # High signal — activated
    high = svc.evaluate_signal(5.0, threshold=0.5, coefficient=2.0)
    assert high.activated


def test_batch_evaluate():
    """batch_evaluate processes all signals."""
    svc = QuorumSensingService()
    results = svc.batch_evaluate(
        [0.0, 0.5, 5.0], threshold=0.5, coefficient=2.0,
    )
    assert len(results) == 3
    assert results[0].response == 0.0
    assert abs(results[1].response - 0.5) < 1e-10
    assert results[2].response > 0.99


def test_serialization():
    """QuorumResponse.to_dict() works correctly."""
    r = QuorumResponse(
        signal=1.0, threshold=0.5, coefficient=2.0,
        response=0.8, activated=True,
    )
    d = r.to_dict()
    assert d["signal"] == 1.0
    assert d["activated"] is True
