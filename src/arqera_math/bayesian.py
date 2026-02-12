"""Bayesian Inference Service.

Provides Bayesian methods for trust and belief updates:
- Beta-binomial model for trust scores
- Bayesian updating with evidence
- Credible interval computation
- Prior selection and calibration

Standalone — no SQLAlchemy or external dependencies.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from arqera_math.constants import get_constant


@dataclass
class BeliefState:
    """Bayesian belief state using Beta distribution."""

    state_id: str = field(default_factory=lambda: str(uuid4()))
    entity_id: str = ""
    entity_type: str = "trust"
    alpha: float = 1.0
    beta: float = 1.0
    mean: float = 0.5
    variance: float = 0.0
    lower_95: float = 0.0
    upper_95: float = 1.0
    total_evidence: int = 0
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "state_id": self.state_id,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "alpha": self.alpha,
            "beta": self.beta,
            "mean": self.mean,
            "variance": self.variance,
            "credible_interval": [self.lower_95, self.upper_95],
            "total_evidence": self.total_evidence,
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class TrustUpdate:
    """A trust update operation."""

    update_id: str = field(default_factory=lambda: str(uuid4()))
    entity_id: str = ""
    prior_alpha: float = 0.0
    prior_beta: float = 0.0
    prior_mean: float = 0.0
    positive_evidence: int = 0
    negative_evidence: int = 0
    posterior_alpha: float = 0.0
    posterior_beta: float = 0.0
    posterior_mean: float = 0.0
    mean_shift: float = 0.0
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "update_id": self.update_id,
            "entity_id": self.entity_id,
            "prior_mean": self.prior_mean,
            "posterior_mean": self.posterior_mean,
            "mean_shift": self.mean_shift,
            "positive_evidence": self.positive_evidence,
            "negative_evidence": self.negative_evidence,
            "updated_at": self.updated_at.isoformat(),
        }


class BayesianTrustService:
    """Service for Bayesian trust management.

    Uses Beta-binomial conjugate model:
    - Prior: Beta(alpha_0, beta_0)
    - Likelihood: Binomial(n, theta)
    - Posterior: Beta(alpha_0 + successes, beta_0 + failures)
    """

    def __init__(self) -> None:
        self._beliefs: dict[str, BeliefState] = {}

    def create_belief(
        self,
        entity_id: str,
        entity_type: str = "trust",
        prior_trust: float = 0.5,
        prior_strength: float | None = None,
    ) -> BeliefState:
        if prior_strength is None:
            prior_strength = get_constant("BAYESIAN_PRIOR_STRENGTH")

        alpha = prior_trust * prior_strength
        beta = (1 - prior_trust) * prior_strength

        belief = BeliefState(
            entity_id=entity_id,
            entity_type=entity_type,
            alpha=alpha,
            beta=beta,
        )
        self._compute_derived(belief)
        self._beliefs[entity_id] = belief
        return belief

    def get_belief(self, entity_id: str) -> BeliefState | None:
        return self._beliefs.get(entity_id)

    def update_trust(
        self,
        entity_id: str,
        positive_evidence: int = 0,
        negative_evidence: int = 0,
    ) -> TrustUpdate | None:
        belief = self._beliefs.get(entity_id)
        if not belief:
            return None

        prior_alpha = belief.alpha
        prior_beta = belief.beta
        prior_mean = belief.mean

        belief.alpha += positive_evidence
        belief.beta += negative_evidence
        belief.total_evidence += positive_evidence + negative_evidence
        belief.updated_at = datetime.now(UTC)

        self._compute_derived(belief)

        return TrustUpdate(
            entity_id=entity_id,
            prior_alpha=prior_alpha,
            prior_beta=prior_beta,
            prior_mean=prior_mean,
            positive_evidence=positive_evidence,
            negative_evidence=negative_evidence,
            posterior_alpha=belief.alpha,
            posterior_beta=belief.beta,
            posterior_mean=belief.mean,
            mean_shift=belief.mean - prior_mean,
        )

    def compute_expected_trust(
        self,
        entity_id: str,
        additional_positive: int = 0,
        additional_negative: int = 0,
    ) -> float:
        belief = self._beliefs.get(entity_id)
        if not belief:
            return 0.5

        new_alpha = belief.alpha + additional_positive
        new_beta = belief.beta + additional_negative
        return new_alpha / (new_alpha + new_beta)

    def compute_credible_interval(
        self,
        alpha: float,
        beta: float,
        confidence: float = 0.95,
    ) -> tuple[float, float]:
        mean = alpha / (alpha + beta)
        var = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1))
        std = math.sqrt(var)

        z = 1.96 if confidence == 0.95 else 2.576 if confidence == 0.99 else 1.645
        lower = max(0, mean - z * std)
        upper = min(1, mean + z * std)
        return lower, upper

    def _compute_derived(self, belief: BeliefState) -> None:
        total = belief.alpha + belief.beta
        belief.mean = belief.alpha / total if total > 0 else 0.5
        belief.variance = (belief.alpha * belief.beta) / (total**2 * (total + 1))
        belief.lower_95, belief.upper_95 = self.compute_credible_interval(belief.alpha, belief.beta)

    def get_all_beliefs(self) -> dict[str, BeliefState]:
        return self._beliefs.copy()


def bayesian_update(
    prior_alpha: float,
    prior_beta: float,
    successes: int,
    failures: int,
) -> tuple[float, float, float]:
    """Simple Bayesian update. Returns (posterior_alpha, posterior_beta, posterior_mean)."""
    post_alpha = prior_alpha + successes
    post_beta = prior_beta + failures
    post_mean = post_alpha / (post_alpha + post_beta)
    return post_alpha, post_beta, post_mean


def trust_from_evidence(
    positive: int,
    negative: int,
    prior_strength: float = 10.0,
    prior_trust: float = 0.5,
) -> float:
    """Compute trust score from evidence counts using Beta-binomial model."""
    alpha = prior_trust * prior_strength + positive
    beta = (1 - prior_trust) * prior_strength + negative
    return alpha / (alpha + beta)
