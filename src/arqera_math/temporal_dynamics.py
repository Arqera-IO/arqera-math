"""Temporal Dynamics Service.

Provides time-series analysis for trust and metrics:
- Trust forecasting via linear regression
- Anomaly detection using z-score method
- Linear trend analysis with least squares

Standalone — no SQLAlchemy or external dependencies.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


@dataclass
class TrustForecast:
    """Trust forecast from linear regression projection."""

    forecast_id: str = field(default_factory=lambda: str(uuid4()))
    entity_id: str = ""
    current_trust: float = 0.0
    forecasted_trust: float = 0.0
    confidence_interval: tuple[float, float] = (0.0, 1.0)
    trend: str = "stable"  # "rising", "stable", "declining"
    forecast_horizon_days: int = 30
    measured_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "forecast_id": self.forecast_id,
            "entity_id": self.entity_id,
            "current_trust": self.current_trust,
            "forecasted_trust": self.forecasted_trust,
            "confidence_interval": list(self.confidence_interval),
            "trend": self.trend,
            "forecast_horizon_days": self.forecast_horizon_days,
            "measured_at": self.measured_at.isoformat(),
        }


@dataclass
class TrendPoint:
    """A single data point in a time series."""

    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    value: float = 0.0


@dataclass
class TrendAnalysis:
    """Linear trend analysis result."""

    analysis_id: str = field(default_factory=lambda: str(uuid4()))
    trend_direction: str = "stable"  # "rising", "stable", "declining"
    slope: float = 0.0
    r_squared: float = 0.0
    points: list[TrendPoint] = field(default_factory=list)
    anomalies: list[int] = field(default_factory=list)
    measured_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "analysis_id": self.analysis_id,
            "trend_direction": self.trend_direction,
            "slope": self.slope,
            "r_squared": self.r_squared,
            "num_points": len(self.points),
            "anomalies": list(self.anomalies),
            "measured_at": self.measured_at.isoformat(),
        }


def forecast_trust(
    history: list[tuple[float, float]],
    horizon_days: int = 30,
) -> TrustForecast:
    """Linear regression on trust history to forecast future trust.

    Uses least squares on (timestamp_days, trust_value) pairs to project
    trust forward by horizon_days.

    Args:
        history: List of (timestamp_days, trust_value) pairs.
        horizon_days: Number of days to forecast ahead.

    Returns:
        TrustForecast with forecast and confidence interval.
    """
    if not history:
        return TrustForecast(
            current_trust=0.5,
            forecasted_trust=0.5,
            confidence_interval=(0.0, 1.0),
            trend="stable",
            forecast_horizon_days=horizon_days,
        )

    sorted_history = sorted(history, key=lambda x: x[0])
    timestamps = [t for t, _ in sorted_history]
    values = [v for _, v in sorted_history]
    current_trust = values[-1]

    if len(history) < 2:
        return TrustForecast(
            entity_id="",
            current_trust=current_trust,
            forecasted_trust=current_trust,
            confidence_interval=(
                max(0.0, current_trust - 0.1),
                min(1.0, current_trust + 0.1),
            ),
            trend="stable",
            forecast_horizon_days=horizon_days,
        )

    slope, intercept, r_squared = linear_trend(
        list(zip(timestamps, values, strict=True))
    )

    # Forecast at last_timestamp + horizon
    last_t = timestamps[-1]
    forecast_t = last_t + horizon_days
    forecasted = slope * forecast_t + intercept

    # Compute residual standard error for confidence interval
    n = len(values)
    residuals = [v - (slope * t + intercept) for t, v in sorted_history]
    sse = sum(r * r for r in residuals)
    se = math.sqrt(sse / (n - 2)) if n > 2 else 0.1

    # 95% confidence interval (approx z=1.96)
    margin = 1.96 * se
    ci_lower = max(0.0, forecasted - margin)
    ci_upper = min(1.0, forecasted + margin)

    # Determine trend
    if abs(slope) < 1e-10:
        trend = "stable"
    elif slope > 0:
        trend = "rising"
    else:
        trend = "declining"

    return TrustForecast(
        entity_id="",
        current_trust=current_trust,
        forecasted_trust=max(0.0, min(1.0, forecasted)),
        confidence_interval=(ci_lower, ci_upper),
        trend=trend,
        forecast_horizon_days=horizon_days,
    )


def detect_anomaly(
    values: list[float],
    threshold_sigma: float = 2.0,
) -> list[int]:
    """Detect anomalies using z-score method.

    A value is anomalous if its absolute z-score exceeds threshold_sigma
    standard deviations from the mean.

    Args:
        values: List of numeric values.
        threshold_sigma: Number of standard deviations to flag.

    Returns:
        List of indices of anomalous values.
    """
    if len(values) < 2:
        return []

    n = len(values)
    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / n
    std = math.sqrt(variance) if variance > 0 else 0.0

    if std == 0.0:
        return []

    return [
        i for i, v in enumerate(values)
        if abs(v - mean) > threshold_sigma * std
    ]


def linear_trend(
    points: list[tuple[float, float]],
) -> tuple[float, float, float]:
    """Least squares linear regression.

    Fits y = slope * x + intercept to the given (x, y) points.

    Args:
        points: List of (x, y) tuples.

    Returns:
        Tuple of (slope, intercept, r_squared).
    """
    n = len(points)
    if n < 2:
        return 0.0, 0.0, 0.0

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    sum_x = sum(xs)
    sum_y = sum(ys)
    sum_xy = sum(x * y for x, y in points)
    sum_x2 = sum(x * x for x in xs)

    denominator = n * sum_x2 - sum_x ** 2
    if denominator == 0:
        return 0.0, sum_y / n, 0.0

    slope = (n * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / n

    # R-squared
    mean_y = sum_y / n
    ss_tot = sum((y - mean_y) ** 2 for y in ys)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in points)
    r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    return slope, intercept, r_squared
