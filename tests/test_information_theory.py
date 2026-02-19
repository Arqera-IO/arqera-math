"""Tests for Information Theory — Renyi Entropy and KL Divergence."""

import math

import pytest

from arqera_math import (
    InformationTheoryService,
    KLDivergenceResult,
    RenyiEntropyResult,
    beta_kl_divergence,
    entropy,
    kl_divergence,
    renyi_entropy,
)


# --- Renyi Entropy tests ---


def test_renyi_collision_entropy_uniform():
    """Collision entropy (alpha=2) of uniform dist = log2(n)."""
    # Uniform over 4 outcomes: H_2 = log2(4) = 2.0
    probs = [0.25, 0.25, 0.25, 0.25]
    h = renyi_entropy(probs, alpha=2.0)
    assert abs(h - 2.0) < 1e-6


def test_renyi_alpha_1_matches_shannon():
    """Renyi at alpha=1 should match Shannon entropy."""
    probs = [0.5, 0.3, 0.2]
    h_renyi = renyi_entropy(probs, alpha=1.0)
    h_shannon = entropy(probs)
    assert abs(h_renyi - h_shannon) < 1e-6


def test_renyi_alpha_0_hartley():
    """Hartley entropy (alpha->0) = log2(support size)."""
    probs = [0.5, 0.3, 0.1, 0.1]
    h = renyi_entropy(probs, alpha=0.0)
    assert abs(h - math.log2(4)) < 1e-6


def test_renyi_min_entropy():
    """Min-entropy (alpha->inf) = -log2(max(p))."""
    probs = [0.5, 0.3, 0.2]
    h = renyi_entropy(probs, alpha=1e7)
    assert abs(h - (-math.log2(0.5))) < 1e-6


def test_renyi_empty():
    """Empty distribution returns 0."""
    assert renyi_entropy([]) == 0.0


def test_renyi_service_method():
    """InformationTheoryService.calculate_renyi_entropy() classifies cases."""
    svc = InformationTheoryService()
    result = svc.calculate_renyi_entropy([0.25, 0.25, 0.25, 0.25], alpha=2.0)
    assert isinstance(result, RenyiEntropyResult)
    assert result.special_case == "collision"
    assert abs(result.entropy - 2.0) < 1e-6


# --- KL Divergence tests ---


def test_kl_same_distribution():
    """KL(P || P) = 0."""
    p = [0.5, 0.3, 0.2]
    assert abs(kl_divergence(p, p)) < 1e-10


def test_kl_asymmetric():
    """KL(P || Q) != KL(Q || P)."""
    p = [0.9, 0.1]
    q = [0.5, 0.5]
    kl_pq = kl_divergence(p, q)
    kl_qp = kl_divergence(q, p)
    assert kl_pq != kl_qp
    assert kl_pq > 0
    assert kl_qp > 0


def test_kl_absolute_continuity_violation():
    """Returns inf when Q(x)=0 where P(x)>0."""
    p = [0.5, 0.5]
    q = [1.0, 0.0]
    assert kl_divergence(p, q) == float("inf")


def test_kl_length_mismatch():
    """Raises ValueError for mismatched lengths."""
    with pytest.raises(ValueError):
        kl_divergence([0.5, 0.5], [0.3, 0.3, 0.4])


def test_kl_service_method():
    """InformationTheoryService.calculate_kl_divergence() wraps result."""
    svc = InformationTheoryService()
    result = svc.calculate_kl_divergence([0.5, 0.5], [0.5, 0.5])
    assert isinstance(result, KLDivergenceResult)
    assert result.is_finite
    assert abs(result.divergence) < 1e-10


def test_kl_service_infinite():
    """Service correctly flags infinite divergence."""
    svc = InformationTheoryService()
    result = svc.calculate_kl_divergence([0.5, 0.5], [1.0, 0.0])
    assert not result.is_finite


# --- Beta KL Divergence tests ---


def test_beta_kl_same_params():
    """KL between identical Beta distributions is ~0."""
    d = beta_kl_divergence(5.0, 5.0, 5.0, 5.0)
    assert abs(d) < 1e-6


def test_beta_kl_different_params():
    """KL between different Beta distributions is > 0."""
    d = beta_kl_divergence(5.0, 5.0, 2.0, 8.0)
    assert d > 0


def test_beta_kl_serialization():
    """Result dataclasses serialize correctly."""
    r = RenyiEntropyResult(entropy=2.0, alpha=2.0, special_case="collision")
    d = r.to_dict()
    assert d["entropy"] == 2.0
    assert d["special_case"] == "collision"

    k = KLDivergenceResult(divergence=0.5, is_finite=True)
    d2 = k.to_dict()
    assert d2["divergence"] == 0.5
    assert d2["is_finite"] is True
