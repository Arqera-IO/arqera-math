"""Mathematical Constants Registry.

Central registry of all mathematical constants used across ARQERA systems.
Standalone — no external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ConstantDomain(StrEnum):
    """Domain/context where constant is used."""

    CONDUCTANCE = "conductance"
    CONTROL = "control"
    GRAPH = "graph"
    ENTROPY = "entropy"
    ECONOMICS = "economics"
    COVERAGE = "coverage"
    SMALL_WORLD = "small_world"
    TRUST = "trust"
    QUEUEING = "queueing"
    BAYESIAN = "bayesian"
    STIGMERGY = "stigmergy"
    STABILITY = "stability"


@dataclass
class MathConstant:
    """A mathematical constant with metadata."""

    name: str
    value: float
    domain: ConstantDomain
    description: str
    min_value: float | None = None
    max_value: float | None = None
    unit: str = ""
    reference: str = ""

    def validate(self, proposed_value: float) -> tuple[bool, str]:
        """Validate a proposed value against bounds."""
        if self.min_value is not None and proposed_value < self.min_value:
            return False, f"Value {proposed_value} below minimum {self.min_value}"
        if self.max_value is not None and proposed_value > self.max_value:
            return False, f"Value {proposed_value} above maximum {self.max_value}"
        return True, "Valid"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "domain": self.domain.value,
            "description": self.description,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "unit": self.unit,
            "reference": self.reference,
        }


MATH_CONSTANTS: dict[str, MathConstant] = {
    # Physarum Dynamics (Conductance)
    "ALPHA_PHYSARUM_REINFORCE": MathConstant(
        name="ALPHA_PHYSARUM_REINFORCE",
        value=0.3,
        domain=ConstantDomain.CONDUCTANCE,
        description="Physarum reinforcement rate for successful paths",
        min_value=0.01,
        max_value=1.0,
        reference="Gravity Architecture: dP/dt = alpha|F| - betaP",
    ),
    "BETA_PHYSARUM_DECAY": MathConstant(
        name="BETA_PHYSARUM_DECAY",
        value=0.05,
        domain=ConstantDomain.CONDUCTANCE,
        description="Physarum decay rate for unused paths",
        min_value=0.001,
        max_value=0.5,
        reference="Gravity Architecture: dP/dt = alpha|F| - betaP",
    ),
    "CONDUCTANCE_MIN": MathConstant(
        name="CONDUCTANCE_MIN",
        value=0.01,
        domain=ConstantDomain.CONDUCTANCE,
        description="Minimum conductance to prevent path elimination",
        min_value=0.001,
        max_value=0.1,
    ),
    "CONDUCTANCE_MAX": MathConstant(
        name="CONDUCTANCE_MAX",
        value=10.0,
        domain=ConstantDomain.CONDUCTANCE,
        description="Maximum conductance to prevent runaway",
        min_value=5.0,
        max_value=100.0,
    ),
    # Graph Theory
    "PAGERANK_DAMPING": MathConstant(
        name="PAGERANK_DAMPING",
        value=0.85,
        domain=ConstantDomain.GRAPH,
        description="PageRank damping factor (random walk probability)",
        min_value=0.5,
        max_value=0.95,
        reference="Original PageRank paper",
    ),
    "PAGERANK_ITERATIONS": MathConstant(
        name="PAGERANK_ITERATIONS",
        value=100,
        domain=ConstantDomain.GRAPH,
        description="Maximum iterations for PageRank convergence",
        min_value=10,
        max_value=1000,
    ),
    "PAGERANK_TOLERANCE": MathConstant(
        name="PAGERANK_TOLERANCE",
        value=1e-6,
        domain=ConstantDomain.GRAPH,
        description="Convergence tolerance for PageRank",
        min_value=1e-10,
        max_value=1e-3,
    ),
    # Small-World Networks
    "MAX_HOPS": MathConstant(
        name="MAX_HOPS",
        value=6,
        domain=ConstantDomain.SMALL_WORLD,
        description="Maximum hops for small-world routing",
        min_value=3,
        max_value=10,
        reference="Six degrees of separation / Milgram",
    ),
    "GREEDY_ROUTING_THRESHOLD": MathConstant(
        name="GREEDY_ROUTING_THRESHOLD",
        value=0.7,
        domain=ConstantDomain.SMALL_WORLD,
        description="Minimum improvement required for greedy routing step",
        min_value=0.5,
        max_value=0.9,
    ),
    # Trust
    "TRUST_TENANT_WEIGHT": MathConstant(
        name="TRUST_TENANT_WEIGHT",
        value=0.7,
        domain=ConstantDomain.TRUST,
        description="Weight for tenant-specific evidence in trust calculation",
        min_value=0.5,
        max_value=0.9,
        reference="70/30 tenant/global formula",
    ),
    "TRUST_GLOBAL_WEIGHT": MathConstant(
        name="TRUST_GLOBAL_WEIGHT",
        value=0.3,
        domain=ConstantDomain.TRUST,
        description="Weight for global reputation in trust calculation",
        min_value=0.1,
        max_value=0.5,
        reference="70/30 tenant/global formula",
    ),
    # Economics
    "NETWORK_VALUE_COEFFICIENT": MathConstant(
        name="NETWORK_VALUE_COEFFICIENT",
        value=1.0,
        domain=ConstantDomain.ECONOMICS,
        description="Base coefficient k in V(n) = k x n x log(n)",
        min_value=0.1,
        max_value=10.0,
        reference="Metcalfe's Law variant",
    ),
    # Coverage
    "COVERAGE_TARGET": MathConstant(
        name="COVERAGE_TARGET",
        value=0.70,
        domain=ConstantDomain.COVERAGE,
        description="Target coverage efficiency (70%)",
        min_value=0.5,
        max_value=0.95,
        reference="Hexagonal tessellation optimal coverage",
    ),
    # Entropy
    "LAMBDA_HEALING_RATE": MathConstant(
        name="LAMBDA_HEALING_RATE",
        value=0.2,
        domain=ConstantDomain.ENTROPY,
        description="Self-healing rate for entropy-based recovery",
        min_value=0.05,
        max_value=0.5,
    ),
    "ENTROPY_PRUNING_THRESHOLD": MathConstant(
        name="ENTROPY_PRUNING_THRESHOLD",
        value=0.5,
        domain=ConstantDomain.ENTROPY,
        description="Minimum entropy for nodes to avoid pruning",
        min_value=0.1,
        max_value=0.9,
    ),
    # Bayesian
    "BAYESIAN_PRIOR_STRENGTH": MathConstant(
        name="BAYESIAN_PRIOR_STRENGTH",
        value=10.0,
        domain=ConstantDomain.BAYESIAN,
        description="Strength of prior belief (pseudo-count)",
        min_value=1.0,
        max_value=100.0,
    ),
    # Precondition weights
    "PRECONDITION_AGE_WEIGHT": MathConstant(
        name="PRECONDITION_AGE_WEIGHT",
        value=0.15,
        domain=ConstantDomain.BAYESIAN,
        description="Weight of age in precondition prior computation",
        min_value=0.0,
        max_value=1.0,
        reference="Precondition system: demographic-informed priors",
    ),
    "PRECONDITION_PROFESSION_WEIGHT": MathConstant(
        name="PRECONDITION_PROFESSION_WEIGHT",
        value=0.25,
        domain=ConstantDomain.BAYESIAN,
        description="Weight of profession in precondition prior computation",
        min_value=0.0,
        max_value=1.0,
        reference="Precondition system: demographic-informed priors",
    ),
    "PRECONDITION_CULTURAL_WEIGHT": MathConstant(
        name="PRECONDITION_CULTURAL_WEIGHT",
        value=0.10,
        domain=ConstantDomain.BAYESIAN,
        description="Weight of cultural context in precondition prior computation",
        min_value=0.0,
        max_value=1.0,
        reference="Precondition system: demographic-informed priors",
    ),
    # Stigmergy
    "STIGMERGY_EVAPORATION_RATE": MathConstant(
        name="STIGMERGY_EVAPORATION_RATE",
        value=0.1,
        domain=ConstantDomain.STIGMERGY,
        description="Pheromone evaporation rate (rho) per time step",
        min_value=0.01,
        max_value=0.5,
        reference="Ant colony optimization: tau(t+1) = (1-rho)*tau(t) + deposit",
    ),
    "PHEROMONE_MIN": MathConstant(
        name="PHEROMONE_MIN",
        value=0.01,
        domain=ConstantDomain.STIGMERGY,
        description="Minimum pheromone intensity",
        min_value=0.001,
        max_value=0.1,
    ),
    "PHEROMONE_MAX": MathConstant(
        name="PHEROMONE_MAX",
        value=10.0,
        domain=ConstantDomain.STIGMERGY,
        description="Maximum pheromone intensity",
        min_value=5.0,
        max_value=100.0,
    ),
    # Quorum Sensing
    "QUORUM_HILL_COEFFICIENT": MathConstant(
        name="QUORUM_HILL_COEFFICIENT",
        value=2.0,
        domain=ConstantDomain.BAYESIAN,
        description="Hill function cooperativity coefficient (n)",
        min_value=1.0,
        max_value=10.0,
        reference="Hill equation: R(S) = S^n / (K^n + S^n)",
    ),
    "QUORUM_THRESHOLD": MathConstant(
        name="QUORUM_THRESHOLD",
        value=0.5,
        domain=ConstantDomain.BAYESIAN,
        description="Hill function half-maximum threshold (K)",
        min_value=0.01,
        max_value=1.0,
        reference="Hill equation: R(K) = 0.5 by definition",
    ),
    "QUORUM_ACTIVATION_THRESHOLD": MathConstant(
        name="QUORUM_ACTIVATION_THRESHOLD",
        value=0.8,
        domain=ConstantDomain.BAYESIAN,
        description="Response level for quorum activation",
        min_value=0.5,
        max_value=0.99,
    ),
    # Lyapunov Stability
    "LYAPUNOV_CONVERGENCE_THRESHOLD": MathConstant(
        name="LYAPUNOV_CONVERGENCE_THRESHOLD",
        value=1e-4,
        domain=ConstantDomain.STABILITY,
        description="Threshold for Lyapunov derivative convergence",
        min_value=1e-8,
        max_value=1e-2,
        reference="Lyapunov stability: V_dot < threshold implies stable",
    ),
    "LYAPUNOV_WINDOW_SIZE": MathConstant(
        name="LYAPUNOV_WINDOW_SIZE",
        value=10,
        domain=ConstantDomain.STABILITY,
        description="State samples for stability analysis",
        min_value=3,
        max_value=100,
    ),
}


def get_constant(name: str) -> float:
    """Get a constant value by name."""
    return MATH_CONSTANTS[name].value


def get_constant_info(name: str) -> MathConstant:
    """Get full constant information by name."""
    return MATH_CONSTANTS[name]


def list_constants_by_domain(domain: ConstantDomain) -> list[MathConstant]:
    """List all constants for a domain."""
    return [c for c in MATH_CONSTANTS.values() if c.domain == domain]


def validate_constant_update(name: str, proposed_value: float) -> tuple[bool, str]:
    """Validate a proposed constant update."""
    if name not in MATH_CONSTANTS:
        return False, f"Unknown constant: {name}"
    return MATH_CONSTANTS[name].validate(proposed_value)
