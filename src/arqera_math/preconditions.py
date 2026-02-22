"""Precondition System — Bayesian priors from demographic/background data.

Encodes demographic information as informed Bayesian priors so the knowledge
graph doesn't start from maximum entropy. A 30s tech founder in London gets
different priors than a 20s student in Tokyo.

Uses Beta distribution pseudo-counts: higher prior_trust × strength = more
confident starting point that still gets overwhelmed by real evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from arqera_math.bayesian import BayesianTrustService, BeliefState
from arqera_math.constants import get_constant


@dataclass
class PreconditionProfile:
    """Demographic and background data for computing informed priors."""

    age_range: str = ""  # "20s", "30s", "40s", etc.
    gender: str = ""
    location: str = ""
    profession: str = ""
    education: str = ""
    culture: str = ""
    interests: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "age_range": self.age_range,
            "gender": self.gender,
            "location": self.location,
            "profession": self.profession,
            "education": self.education,
            "culture": self.culture,
            "interests": self.interests,
            "metadata": self.metadata,
        }


# Domain prior tables — keyed by profession category
_PROFESSION_DOMAIN_PRIORS: dict[str, dict[str, float]] = {
    "founder": {
        "career": 0.85,
        "finance": 0.70,
        "health": 0.40,
        "family": 0.45,
        "social": 0.60,
        "growth": 0.75,
        "fun": 0.35,
        "environment": 0.50,
    },
    "engineer": {
        "career": 0.75,
        "finance": 0.55,
        "health": 0.45,
        "family": 0.50,
        "social": 0.45,
        "growth": 0.70,
        "fun": 0.50,
        "environment": 0.50,
    },
    "creative": {
        "career": 0.60,
        "finance": 0.40,
        "health": 0.50,
        "family": 0.50,
        "social": 0.65,
        "growth": 0.70,
        "fun": 0.70,
        "environment": 0.55,
    },
    "default": {
        "career": 0.50,
        "finance": 0.50,
        "health": 0.50,
        "family": 0.50,
        "social": 0.50,
        "growth": 0.50,
        "fun": 0.50,
        "environment": 0.50,
    },
}

# Age adjustments (delta applied to base prior)
_AGE_ADJUSTMENTS: dict[str, dict[str, float]] = {
    "20s": {"career": -0.05, "finance": -0.10, "health": 0.10, "fun": 0.10, "growth": 0.05},
    "30s": {"career": 0.05, "finance": 0.05, "family": 0.05},
    "40s": {"career": 0.05, "finance": 0.10, "health": -0.05, "family": 0.10},
    "50s": {"finance": 0.10, "health": -0.10, "family": 0.10, "fun": 0.05},
}

# Entity type base priors by profession
_ENTITY_TYPE_PRIORS: dict[str, dict[str, float]] = {
    "founder": {
        "person": 0.65,
        "organization": 0.80,
        "project": 0.75,
        "document": 0.60,
        "event": 0.55,
        "goal": 0.70,
        "asset": 0.65,
    },
    "default": {
        "person": 0.60,
        "organization": 0.50,
        "project": 0.50,
        "document": 0.50,
        "event": 0.50,
        "goal": 0.50,
        "asset": 0.50,
    },
}


def _classify_profession(profession: str) -> str:
    """Classify a profession string into a category."""
    prof_lower = profession.lower()
    if any(kw in prof_lower for kw in ("founder", "ceo", "cto", "entrepreneur", "co-founder")):
        return "founder"
    if any(kw in prof_lower for kw in ("engineer", "developer", "programmer", "architect")):
        return "engineer"
    if any(kw in prof_lower for kw in ("designer", "artist", "writer", "creative", "musician")):
        return "creative"
    return "default"


def compute_domain_priors(profile: PreconditionProfile) -> dict[str, BeliefState]:
    """Compute informed Bayesian priors for each Wheel of Life domain.

    Returns a dict of domain_name → BeliefState with priors shaped by
    the profile's demographics. These are starting points that real
    evidence will quickly overwhelm.
    """
    age_weight = get_constant("PRECONDITION_AGE_WEIGHT")
    profession_weight = get_constant("PRECONDITION_PROFESSION_WEIGHT")
    cultural_weight = get_constant("PRECONDITION_CULTURAL_WEIGHT")

    prof_category = _classify_profession(profile.profession)
    base_priors = _PROFESSION_DOMAIN_PRIORS.get(prof_category, _PROFESSION_DOMAIN_PRIORS["default"])

    # Apply age adjustments
    age_deltas = _AGE_ADJUSTMENTS.get(profile.age_range, {})

    svc = BayesianTrustService()
    result: dict[str, BeliefState] = {}

    for domain, base_prior in base_priors.items():
        # Weighted combination: profession contributes most, then age, then culture
        adjusted = base_prior

        # Age adjustment (weighted)
        age_delta = age_deltas.get(domain, 0.0)
        adjusted += age_delta * (age_weight / profession_weight) if profession_weight > 0 else 0.0

        # Interest boost: if domain matches an interest, nudge up
        domain_interests = [i for i in profile.interests if domain in i.lower()]
        if domain_interests:
            adjusted += 0.05 * len(domain_interests)

        # Cultural weight is reserved for future cultural adjustments
        # Currently applies a small stabilization toward the base
        adjusted = adjusted * (1 - cultural_weight) + base_prior * cultural_weight

        # Clamp to valid probability range
        adjusted = max(0.05, min(0.95, adjusted))

        # Use lower prior strength so real evidence overwhelms quickly
        prior_strength = get_constant("BAYESIAN_PRIOR_STRENGTH") * 0.5

        belief = svc.create_belief(
            entity_id=f"precondition-{domain}",
            entity_type="domain_prior",
            prior_trust=adjusted,
            prior_strength=prior_strength,
        )
        result[domain] = belief

    return result


def compute_entity_prior(entity_type: str, profile: PreconditionProfile) -> float:
    """Compute a trust prior for an entity type given background context.

    Returns a float 0-1 representing how much to trust this entity type
    before any real evidence. A founder's organization nodes get higher
    priors than a student's.
    """
    prof_category = _classify_profession(profile.profession)
    type_priors = _ENTITY_TYPE_PRIORS.get(prof_category, _ENTITY_TYPE_PRIORS["default"])
    return type_priors.get(entity_type.lower(), 0.5)
