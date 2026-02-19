"""Tests for Bayesian Trust Service."""

from arqera_math import (
    BayesianTrustService,
    FisherInformationResult,
    bayesian_update,
    cramer_rao_bound,
    fisher_information,
    trust_from_evidence,
)


def test_create_belief_default():
    svc = BayesianTrustService()
    belief = svc.create_belief("entity-1")
    assert belief.entity_id == "entity-1"
    assert 0.49 < belief.mean < 0.51  # Default prior 0.5
    assert belief.alpha > 0
    assert belief.beta > 0


def test_create_belief_high_prior():
    svc = BayesianTrustService()
    belief = svc.create_belief("entity-2", prior_trust=0.9)
    assert belief.mean > 0.85


def test_update_trust_positive():
    svc = BayesianTrustService()
    svc.create_belief("entity-3", prior_trust=0.5)
    update = svc.update_trust("entity-3", positive_evidence=5)
    assert update is not None
    assert update.posterior_mean > update.prior_mean
    assert update.mean_shift > 0


def test_update_trust_negative():
    svc = BayesianTrustService()
    svc.create_belief("entity-4", prior_trust=0.5)
    update = svc.update_trust("entity-4", negative_evidence=5)
    assert update is not None
    assert update.posterior_mean < update.prior_mean


def test_update_trust_unknown_entity():
    svc = BayesianTrustService()
    assert svc.update_trust("nonexistent", positive_evidence=1) is None


def test_credible_interval():
    svc = BayesianTrustService()
    lower, upper = svc.compute_credible_interval(10.0, 10.0)
    assert 0 <= lower < 0.5
    assert 0.5 < upper <= 1.0
    assert lower < upper


def test_bayesian_update_utility():
    alpha, beta, mean = bayesian_update(5.0, 5.0, 3, 1)
    assert alpha == 8.0
    assert beta == 6.0
    assert abs(mean - 8.0 / 14.0) < 1e-6


def test_trust_from_evidence():
    # With equal evidence, should stay near prior
    trust = trust_from_evidence(5, 5)
    assert 0.4 < trust < 0.6

    # Strong positive evidence pushes trust up
    trust = trust_from_evidence(50, 0)
    assert trust > 0.8


# --- Fisher Information tests ---


def test_fisher_information_symmetric():
    """Symmetric Beta(10,10) — theta=0.5, n=20, I = 20/(0.5*0.5) = 80."""
    fi = fisher_information(10.0, 10.0)
    assert abs(fi - 80.0) < 1e-6


def test_fisher_information_edge_cases():
    """Theta near 0 or 1 should return 0 (degenerate)."""
    # All successes: theta=1, denominator=0
    assert fisher_information(10.0, 0.0) == 0.0
    # All failures: theta=0, denominator=0
    assert fisher_information(0.0, 10.0) == 0.0
    # Zero evidence
    assert fisher_information(0.0, 0.0) == 0.0


def test_cramer_rao_decreases_with_evidence():
    """CRB should decrease as we accumulate more evidence."""
    crb_small = cramer_rao_bound(5.0, 5.0)
    crb_large = cramer_rao_bound(50.0, 50.0)
    assert crb_large < crb_small


def test_fisher_information_result_serialization():
    """FisherInformationResult.to_dict() round-trips correctly."""
    result = FisherInformationResult(
        alpha=10.0,
        beta=10.0,
        fisher_information=80.0,
        cramer_rao_bound=0.0125,
        sample_size=20,
        precision=80.0,
    )
    d = result.to_dict()
    assert d["alpha"] == 10.0
    assert d["fisher_information"] == 80.0
    assert d["cramer_rao_bound"] == 0.0125


def test_compute_fisher_information_service():
    """BayesianTrustService.compute_fisher_information() works end-to-end."""
    svc = BayesianTrustService()
    svc.create_belief("entity-fi", prior_trust=0.5, prior_strength=20.0)
    result = svc.compute_fisher_information("entity-fi")
    assert result is not None
    assert result.fisher_information > 0
    assert result.cramer_rao_bound > 0
    assert result.sample_size == 20

    # Unknown entity returns None
    assert svc.compute_fisher_information("nonexistent") is None
