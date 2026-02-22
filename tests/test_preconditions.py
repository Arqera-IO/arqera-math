"""Tests for the Precondition System."""

from arqera_math import PreconditionProfile, compute_domain_priors, compute_entity_prior


def test_profile_creation():
    profile = PreconditionProfile(
        age_range="30s",
        gender="male",
        location="London",
        profession="Founder/CEO",
        education="Engineering",
    )
    assert profile.age_range == "30s"
    assert profile.profession == "Founder/CEO"


def test_profile_to_dict():
    profile = PreconditionProfile(age_range="30s", profession="Engineer")
    d = profile.to_dict()
    assert d["age_range"] == "30s"
    assert d["profession"] == "Engineer"
    assert isinstance(d["interests"], list)


def test_compute_domain_priors_founder():
    profile = PreconditionProfile(
        age_range="30s",
        profession="Founder/CEO",
    )
    priors = compute_domain_priors(profile)

    # Should return all 8 domains
    assert len(priors) == 8
    assert "career" in priors
    assert "health" in priors

    # Founder should have high career prior, lower health
    assert priors["career"].mean > 0.7
    assert priors["health"].mean < priors["career"].mean


def test_compute_domain_priors_engineer():
    profile = PreconditionProfile(
        age_range="20s",
        profession="Software Developer",
    )
    priors = compute_domain_priors(profile)
    assert len(priors) == 8

    # Engineer should have solid career but not as high as founder
    assert priors["career"].mean > 0.5
    assert priors["growth"].mean > 0.5


def test_compute_domain_priors_default():
    profile = PreconditionProfile(
        age_range="40s",
        profession="Accountant",
    )
    priors = compute_domain_priors(profile)
    assert len(priors) == 8

    # Default profession — all domains near 0.5
    for belief in priors.values():
        assert 0.3 < belief.mean < 0.7


def test_compute_domain_priors_with_interests():
    profile = PreconditionProfile(
        age_range="30s",
        profession="Founder",
        interests=["health and fitness", "career development"],
    )
    priors_with = compute_domain_priors(profile)

    profile_without = PreconditionProfile(
        age_range="30s",
        profession="Founder",
        interests=[],
    )
    priors_without = compute_domain_priors(profile_without)

    # Interests should boost the matching domain slightly
    assert priors_with["health"].mean >= priors_without["health"].mean


def test_compute_domain_priors_all_valid():
    profile = PreconditionProfile(age_range="30s", profession="Founder")
    priors = compute_domain_priors(profile)

    for domain, belief in priors.items():
        assert 0.0 < belief.mean < 1.0, f"{domain} mean out of range: {belief.mean}"
        assert belief.alpha > 0, f"{domain} alpha must be positive"
        assert belief.beta > 0, f"{domain} beta must be positive"


def test_compute_entity_prior_founder():
    profile = PreconditionProfile(profession="CEO")
    assert compute_entity_prior("organization", profile) > 0.7
    assert compute_entity_prior("project", profile) > 0.6
    assert compute_entity_prior("person", profile) > 0.5


def test_compute_entity_prior_default():
    profile = PreconditionProfile(profession="Teacher")
    prior = compute_entity_prior("organization", profile)
    assert prior == 0.5  # Default profession, default entity prior


def test_compute_entity_prior_unknown_type():
    profile = PreconditionProfile(profession="Founder")
    prior = compute_entity_prior("unknown_type", profile)
    assert prior == 0.5  # Falls back to 0.5


def test_empty_profile():
    profile = PreconditionProfile()
    priors = compute_domain_priors(profile)
    assert len(priors) == 8

    # All should be near 0.5 (uninformative)
    for belief in priors.values():
        assert 0.4 < belief.mean < 0.6
