"""Quorum Sensing Service.

Provides biological threshold functions for collective decision-making:
- Hill function for smooth activation/deactivation curves
- Signal evaluation with configurable cooperativity
- Batch processing for multiple signals

Standalone — no external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from arqera_math.constants import get_constant


@dataclass
class QuorumResponse:
    """Result of a quorum sensing evaluation."""

    signal: float = 0.0
    threshold: float = 0.0
    coefficient: float = 0.0
    response: float = 0.0
    activated: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal": self.signal,
            "threshold": self.threshold,
            "coefficient": self.coefficient,
            "response": self.response,
            "activated": self.activated,
        }


def hill_function(
    signal: float,
    threshold: float | None = None,
    coefficient: float | None = None,
) -> float:
    """Compute Hill function response.

    R(S) = S^n / (K^n + S^n)

    where S is signal strength, K is threshold (half-maximum),
    and n is the Hill coefficient (cooperativity).

    Returns value in [0, 1].
    """
    if threshold is None:
        threshold = get_constant("QUORUM_THRESHOLD")
    if coefficient is None:
        coefficient = get_constant("QUORUM_HILL_COEFFICIENT")

    if signal <= 0:
        return 0.0
    if threshold <= 0:
        return 1.0

    s_n = signal**coefficient
    k_n = threshold**coefficient
    return s_n / (k_n + s_n)


class QuorumSensingService:
    """Service for quorum sensing evaluation.

    Models collective threshold behavior using the Hill equation.
    Replaces hard thresholds with smooth biological S-curves.
    """

    def evaluate_signal(
        self,
        signal: float,
        threshold: float | None = None,
        coefficient: float | None = None,
    ) -> QuorumResponse:
        """Evaluate a single signal against the quorum threshold."""
        if threshold is None:
            threshold = get_constant("QUORUM_THRESHOLD")
        if coefficient is None:
            coefficient = get_constant("QUORUM_HILL_COEFFICIENT")

        response = hill_function(signal, threshold, coefficient)
        activation_threshold = get_constant("QUORUM_ACTIVATION_THRESHOLD")

        return QuorumResponse(
            signal=signal,
            threshold=threshold,
            coefficient=coefficient,
            response=response,
            activated=response >= activation_threshold,
        )

    def batch_evaluate(
        self,
        signals: list[float],
        threshold: float | None = None,
        coefficient: float | None = None,
    ) -> list[QuorumResponse]:
        """Evaluate multiple signals."""
        return [
            self.evaluate_signal(s, threshold, coefficient) for s in signals
        ]
