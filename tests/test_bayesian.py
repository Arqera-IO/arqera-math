"""Tests for Bayesian Trust Service."""

from arqera_math import BayesianTrustService, bayesian_update, trust_from_evidence


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
