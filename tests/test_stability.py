"""Tests for Lyapunov Stability Analysis."""

import pytest

from arqera_math import (
    StabilityAnalysis,
    StabilityService,
    check_stability,
    lyapunov_function,
)


def test_lyapunov_at_equilibrium():
    """V(equilibrium) = 0."""
    eq = [1.0, 2.0, 3.0]
    assert lyapunov_function(eq, eq) == 0.0


def test_lyapunov_away_from_equilibrium():
    """V(state != equilibrium) > 0."""
    state = [1.5, 2.5, 3.5]
    eq = [1.0, 2.0, 3.0]
    v = lyapunov_function(state, eq)
    assert v > 0


def test_lyapunov_dimension_mismatch():
    """Dimension mismatch raises ValueError."""
    with pytest.raises(ValueError):
        lyapunov_function([1.0, 2.0], [1.0, 2.0, 3.0])


def test_converging_sequence_is_stable():
    """A sequence converging to equilibrium is stable."""
    eq = [0.0, 0.0]
    # Each step moves 50% closer to equilibrium
    history = [
        [1.0, 1.0],
        [0.5, 0.5],
        [0.25, 0.25],
        [0.125, 0.125],
        [0.0625, 0.0625],
        [0.03125, 0.03125],
        [0.015625, 0.015625],
        [0.0078125, 0.0078125],
        [0.00390625, 0.00390625],
        [0.001953125, 0.001953125],
        [0.0009765625, 0.0009765625],
        [0.00048828125, 0.00048828125],
    ]
    result = check_stability(history, eq)
    assert result.is_stable
    assert result.convergence_rate > 0


def test_diverging_sequence_is_unstable():
    """A diverging sequence is not stable."""
    eq = [0.0, 0.0]
    # Each step moves further from equilibrium
    history = [
        [0.1, 0.1],
        [0.2, 0.2],
        [0.4, 0.4],
        [0.8, 0.8],
        [1.6, 1.6],
        [3.2, 3.2],
        [6.4, 6.4],
        [12.8, 12.8],
        [25.6, 25.6],
        [51.2, 51.2],
        [102.4, 102.4],
        [204.8, 204.8],
    ]
    result = check_stability(history, eq)
    assert not result.is_stable


def test_oscillating_sequence_is_unstable():
    """An oscillating sequence is not stable."""
    eq = [0.0]
    history = [
        [1.0], [-1.0], [1.0], [-1.0], [1.0], [-1.0],
        [1.0], [-1.0], [1.0], [-1.0], [1.0], [-1.0],
    ]
    result = check_stability(history, eq)
    assert not result.is_stable


def test_serialization():
    """StabilityAnalysis.to_dict() works correctly."""
    r = StabilityAnalysis(
        lyapunov_value=0.5, derivative=-0.01,
        is_stable=True, convergence_rate=0.01, window_size=10,
    )
    d = r.to_dict()
    assert d["lyapunov_value"] == 0.5
    assert d["is_stable"] is True


def test_stability_service():
    """StabilityService delegates to standalone functions."""
    svc = StabilityService()
    v = svc.lyapunov_function([1.0, 2.0], [0.0, 0.0])
    assert v == 2.5  # 0.5 * (1^2 + 2^2)

    result = svc.check_stability(
        [[1.0], [0.5], [0.25], [0.125]], [0.0],
    )
    assert result.is_stable
