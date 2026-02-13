"""Tests for Temporal Dynamics Service."""

from arqera_math import (
    TrendAnalysis,
    TrustForecast,
    detect_anomaly,
    forecast_trust,
    linear_trend,
)


def test_forecast_trust_rising():
    """Rising trust history should produce rising trend."""
    history = [(float(i), 0.3 + i * 0.05) for i in range(10)]
    result = forecast_trust(history)

    assert isinstance(result, TrustForecast)
    assert result.trend == "rising"
    assert result.current_trust == history[-1][1]
    assert result.forecasted_trust > result.current_trust


def test_forecast_trust_declining():
    """Declining trust history should produce declining trend."""
    history = [(float(i), 0.9 - i * 0.05) for i in range(10)]
    result = forecast_trust(history)

    assert result.trend == "declining"
    assert result.current_trust == history[-1][1]
    assert result.forecasted_trust < result.current_trust


def test_forecast_trust_empty():
    """Empty history should return stable default."""
    result = forecast_trust([])
    assert result.current_trust == 0.5
    assert result.trend == "stable"
    assert result.forecast_horizon_days == 30


def test_forecast_trust_single_point():
    """Single point should return stable forecast."""
    result = forecast_trust([(0.0, 0.7)])
    assert result.current_trust == 0.7
    assert result.trend == "stable"


def test_forecast_trust_confidence_interval():
    """Forecast should include valid confidence interval."""
    history = [(float(i), 0.5 + i * 0.01) for i in range(20)]
    result = forecast_trust(history, horizon_days=10)

    ci_lower, ci_upper = result.confidence_interval
    assert 0.0 <= ci_lower <= ci_upper <= 1.0
    assert result.forecast_horizon_days == 10


def test_detect_anomaly_clear_outliers():
    """Clear outliers should be detected."""
    values = [10.0, 10.1, 9.9, 10.0, 10.2, 9.8, 10.0, 50.0, 10.1, -30.0]
    anomalies = detect_anomaly(values)

    assert 7 in anomalies  # 50.0 is an outlier
    assert 9 in anomalies  # -30.0 is an outlier
    assert 0 not in anomalies
    assert 1 not in anomalies


def test_detect_anomaly_no_outliers():
    """Uniform values should produce no anomalies."""
    values = [5.0, 5.1, 4.9, 5.0, 5.05]
    anomalies = detect_anomaly(values)
    assert len(anomalies) == 0


def test_detect_anomaly_single_value():
    """Single value should return empty list."""
    assert detect_anomaly([5.0]) == []


def test_linear_trend_rising():
    """Perfect linear increase should yield slope and R^2 = 1."""
    # y = 2x + 1
    points = [(float(i), 2.0 * i + 1.0) for i in range(5)]
    slope, intercept, r_squared = linear_trend(points)

    assert abs(slope - 2.0) < 1e-6
    assert abs(intercept - 1.0) < 1e-6
    assert abs(r_squared - 1.0) < 1e-6


def test_linear_trend_declining():
    """Perfect linear decrease should yield negative slope."""
    # y = 10 - x
    points = [(float(i), 10.0 - i) for i in range(5)]
    slope, intercept, r_squared = linear_trend(points)

    assert abs(slope - (-1.0)) < 1e-6
    assert abs(r_squared - 1.0) < 1e-6


def test_linear_trend_single_point():
    """Single point should return zero slope."""
    slope, intercept, r_squared = linear_trend([(0.0, 42.0)])
    assert slope == 0.0
    assert r_squared == 0.0


def test_trust_forecast_to_dict():
    """TrustForecast.to_dict serializes all fields."""
    forecast = TrustForecast(
        entity_id="e1",
        current_trust=0.5,
        forecasted_trust=0.7,
        confidence_interval=(0.4, 0.9),
        trend="rising",
    )
    d = forecast.to_dict()
    assert d["entity_id"] == "e1"
    assert d["current_trust"] == 0.5
    assert d["forecasted_trust"] == 0.7
    assert d["confidence_interval"] == [0.4, 0.9]
    assert d["trend"] == "rising"
    assert "forecast_id" in d


def test_trend_analysis_to_dict():
    """TrendAnalysis.to_dict serializes all fields."""
    analysis = TrendAnalysis(
        trend_direction="rising",
        slope=1.5,
        r_squared=0.95,
        anomalies=[3, 7],
    )
    d = analysis.to_dict()
    assert d["trend_direction"] == "rising"
    assert d["slope"] == 1.5
    assert d["r_squared"] == 0.95
    assert d["anomalies"] == [3, 7]
    assert "analysis_id" in d
