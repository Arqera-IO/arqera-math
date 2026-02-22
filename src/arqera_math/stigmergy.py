"""Stigmergy Service.

Provides pheromone-based indirect communication for route optimization:
- Pheromone trail deposit and evaporation
- Gradient computation for route selection
- Metrics aggregation across trails

Standalone — no external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from arqera_math.constants import get_constant


@dataclass
class PheromoneTrail:
    """A pheromone trail on a graph edge."""

    trail_id: str = ""
    edge_id: str = ""
    intensity: float = 0.0
    deposit_time: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "trail_id": self.trail_id,
            "edge_id": self.edge_id,
            "intensity": self.intensity,
            "deposit_time": self.deposit_time.isoformat(),
        }


@dataclass
class StigmergyMetrics:
    """Aggregate metrics across all pheromone trails."""

    total_trails: int = 0
    avg_intensity: float = 0.0
    max_intensity: float = 0.0
    min_intensity: float = 0.0
    active_trails: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_trails": self.total_trails,
            "avg_intensity": self.avg_intensity,
            "max_intensity": self.max_intensity,
            "min_intensity": self.min_intensity,
            "active_trails": self.active_trails,
        }


def update_pheromone(
    current: float,
    deposit: float,
    evaporation_rate: float | None = None,
) -> float:
    """Update pheromone intensity with evaporation and deposit.

    tau(t+1) = (1 - rho) * tau(t) + deposit

    Result is clamped to [PHEROMONE_MIN, PHEROMONE_MAX].
    """
    if evaporation_rate is None:
        evaporation_rate = get_constant("STIGMERGY_EVAPORATION_RATE")

    new_intensity = (1 - evaporation_rate) * current + deposit
    pmin = get_constant("PHEROMONE_MIN")
    pmax = get_constant("PHEROMONE_MAX")
    return max(pmin, min(pmax, new_intensity))


def pheromone_gradient(
    intensities: dict[str, float],
) -> list[tuple[str, float]]:
    """Compute pheromone gradient — edges sorted by descending intensity."""
    return sorted(intensities.items(), key=lambda x: x[1], reverse=True)


class StigmergyService:
    """Service for pheromone-based stigmergic communication.

    Models indirect coordination through environmental modification:
    - Successful routes deposit pheromone
    - All trails evaporate over time
    - Gradient guides future routing decisions
    """

    def __init__(self) -> None:
        self._trails: dict[str, PheromoneTrail] = {}
        self._trail_counter: int = 0

    def deposit_pheromone(
        self,
        edge_id: str,
        deposit_amount: float,
    ) -> PheromoneTrail:
        """Deposit pheromone on an edge. Creates trail if new."""
        existing = self._trails.get(edge_id)
        current = existing.intensity if existing else 0.0

        new_intensity = update_pheromone(current, deposit_amount)

        self._trail_counter += 1
        trail = PheromoneTrail(
            trail_id=f"trail-{self._trail_counter}",
            edge_id=edge_id,
            intensity=new_intensity,
        )
        self._trails[edge_id] = trail
        return trail

    def evaporate(self, evaporation_rate: float | None = None) -> int:
        """Evaporate all trails. Returns number of trails affected."""
        if evaporation_rate is None:
            evaporation_rate = get_constant("STIGMERGY_EVAPORATION_RATE")

        pmin = get_constant("PHEROMONE_MIN")
        affected = 0

        for trail in self._trails.values():
            old = trail.intensity
            trail.intensity = max(pmin, (1 - evaporation_rate) * trail.intensity)
            if trail.intensity != old:
                affected += 1

        return affected

    def get_trail(self, edge_id: str) -> PheromoneTrail | None:
        """Get trail for an edge."""
        return self._trails.get(edge_id)

    def get_metrics(self) -> StigmergyMetrics:
        """Compute aggregate metrics across all trails."""
        if not self._trails:
            return StigmergyMetrics()

        intensities = [t.intensity for t in self._trails.values()]
        pmin = get_constant("PHEROMONE_MIN")
        active = sum(1 for i in intensities if i > pmin)

        return StigmergyMetrics(
            total_trails=len(self._trails),
            avg_intensity=sum(intensities) / len(intensities),
            max_intensity=max(intensities),
            min_intensity=min(intensities),
            active_trails=active,
        )

    def get_pheromone_gradient(self, edge_ids: list[str]) -> list[tuple[str, float]]:
        """Get pheromone gradient for a subset of edges."""
        intensities = {}
        for eid in edge_ids:
            trail = self._trails.get(eid)
            intensities[eid] = trail.intensity if trail else 0.0
        return pheromone_gradient(intensities)
