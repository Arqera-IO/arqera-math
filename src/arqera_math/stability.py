"""Lyapunov Stability Analysis.

Provides convergence verification for dynamical systems:
- Lyapunov function computation (distance from equilibrium)
- Stability checking via derivative analysis
- Convergence rate estimation

Standalone — no external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from arqera_math.constants import get_constant


@dataclass
class StabilityAnalysis:
    """Result of a Lyapunov stability analysis."""

    lyapunov_value: float = 0.0
    derivative: float = 0.0
    is_stable: bool = False
    convergence_rate: float = 0.0
    window_size: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "lyapunov_value": self.lyapunov_value,
            "derivative": self.derivative,
            "is_stable": self.is_stable,
            "convergence_rate": self.convergence_rate,
            "window_size": self.window_size,
        }


def lyapunov_function(
    state: list[float], equilibrium: list[float]
) -> float:
    """Compute Lyapunov function value.

    V(P) = 0.5 * sum((P_j - P_j*)^2)

    Measures squared distance from equilibrium.
    V = 0 at equilibrium, V > 0 elsewhere.
    """
    if len(state) != len(equilibrium):
        raise ValueError(
            f"State dimension {len(state)} != equilibrium dimension "
            f"{len(equilibrium)}"
        )
    return 0.5 * sum(
        (s - e) ** 2 for s, e in zip(state, equilibrium, strict=True)
    )


def check_stability(
    state_history: list[list[float]],
    equilibrium: list[float] | None = None,
) -> StabilityAnalysis:
    """Check system stability from a history of state observations.

    Computes V at each step, then checks if V_dot (derivative) is
    consistently negative, indicating convergence.

    If no equilibrium is provided, uses the last state as target.
    """
    if not state_history or len(state_history) < 2:
        return StabilityAnalysis(is_stable=False, window_size=0)

    if equilibrium is None:
        equilibrium = state_history[-1]

    window_size = int(get_constant("LYAPUNOV_WINDOW_SIZE"))
    threshold = get_constant("LYAPUNOV_CONVERGENCE_THRESHOLD")

    # Compute V at each time step
    v_values = [lyapunov_function(s, equilibrium) for s in state_history]

    # Compute derivatives (V_dot approximation)
    v_dots = [
        v_values[i + 1] - v_values[i]
        for i in range(len(v_values) - 1)
    ]

    # Use the last window_size derivatives for stability assessment
    recent_window = min(window_size, len(v_dots))
    recent_dots = v_dots[-recent_window:]

    # Stable if V is near zero (at equilibrium) OR all recent
    # derivatives are strictly negative (converging toward equilibrium)
    at_equilibrium = v_values[-1] <= threshold
    converging = all(d < 0 for d in recent_dots)
    is_stable = at_equilibrium or converging

    # Convergence rate: average of recent negative derivatives
    avg_derivative = sum(recent_dots) / len(recent_dots) if recent_dots else 0.0

    return StabilityAnalysis(
        lyapunov_value=v_values[-1],
        derivative=avg_derivative,
        is_stable=is_stable,
        convergence_rate=abs(avg_derivative) if is_stable else 0.0,
        window_size=recent_window,
    )


class StabilityService:
    """Service for Lyapunov stability monitoring.

    Tracks system state over time and provides stability analysis.
    """

    def lyapunov_function(
        self, state: list[float], equilibrium: list[float]
    ) -> float:
        """Compute Lyapunov function value."""
        return lyapunov_function(state, equilibrium)

    def check_stability(
        self,
        state_history: list[list[float]],
        equilibrium: list[float] | None = None,
    ) -> StabilityAnalysis:
        """Check system stability from state history."""
        return check_stability(state_history, equilibrium)
