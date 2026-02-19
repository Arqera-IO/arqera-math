"""Tests for Stigmergy Service."""

from arqera_math import (
    PheromoneTrail,
    StigmergyMetrics,
    StigmergyService,
    pheromone_gradient,
    update_pheromone,
)
from arqera_math.constants import get_constant


def test_deposit_increases_intensity():
    """Depositing pheromone increases trail intensity."""
    svc = StigmergyService()
    trail = svc.deposit_pheromone("edge-1", 1.0)
    assert trail.intensity > 0
    assert trail.edge_id == "edge-1"


def test_evaporate_decreases_intensity():
    """Evaporation decreases intensity but respects PHEROMONE_MIN."""
    svc = StigmergyService()
    svc.deposit_pheromone("edge-1", 5.0)
    svc.evaporate()
    trail = svc.get_trail("edge-1")
    assert trail is not None
    assert trail.intensity < 5.0
    assert trail.intensity >= get_constant("PHEROMONE_MIN")


def test_update_pheromone_formula():
    """Verify tau(t+1) = (1-rho)*tau(t) + deposit."""
    # rho=0.1, current=2.0, deposit=1.0
    # expected = (1-0.1)*2.0 + 1.0 = 1.8 + 1.0 = 2.8
    result = update_pheromone(2.0, 1.0, evaporation_rate=0.1)
    assert abs(result - 2.8) < 1e-6


def test_update_pheromone_bounds_min():
    """Pheromone is clamped to PHEROMONE_MIN."""
    result = update_pheromone(0.0, 0.0, evaporation_rate=0.5)
    assert result == get_constant("PHEROMONE_MIN")


def test_update_pheromone_bounds_max():
    """Pheromone is clamped to PHEROMONE_MAX."""
    result = update_pheromone(9.0, 5.0, evaporation_rate=0.0)
    pmax = get_constant("PHEROMONE_MAX")
    assert result == pmax


def test_gradient_descending_order():
    """Pheromone gradient returns edges in descending intensity order."""
    intensities = {"a": 1.0, "b": 5.0, "c": 3.0}
    grad = pheromone_gradient(intensities)
    assert grad[0] == ("b", 5.0)
    assert grad[1] == ("c", 3.0)
    assert grad[2] == ("a", 1.0)


def test_metrics_aggregate():
    """StigmergyService.get_metrics() aggregates correctly."""
    svc = StigmergyService()
    svc.deposit_pheromone("e1", 2.0)
    svc.deposit_pheromone("e2", 4.0)
    metrics = svc.get_metrics()
    assert metrics.total_trails == 2
    assert metrics.max_intensity >= metrics.avg_intensity
    assert metrics.min_intensity <= metrics.avg_intensity


def test_serialization():
    """Dataclasses serialize via to_dict()."""
    trail = PheromoneTrail(trail_id="t1", edge_id="e1", intensity=2.5)
    d = trail.to_dict()
    assert d["trail_id"] == "t1"
    assert d["intensity"] == 2.5

    metrics = StigmergyMetrics(
        total_trails=3, avg_intensity=2.0, max_intensity=5.0,
        min_intensity=0.5, active_trails=2,
    )
    d2 = metrics.to_dict()
    assert d2["total_trails"] == 3
    assert d2["active_trails"] == 2
