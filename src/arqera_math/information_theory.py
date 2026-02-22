"""Information Theory Service.

Provides information-theoretic analysis:
- Shannon entropy calculation
- Knowledge compression and pruning
- Mutual information
- Information gain from evidence

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
class NodeEntropy:
    """Entropy calculation for a knowledge node."""

    node_id: str
    node_name: str = ""
    entropy: float = 0.0
    edge_count: int = 0
    edge_distribution: list[float] = field(default_factory=list)
    is_prunable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_name": self.node_name,
            "entropy": self.entropy,
            "edge_count": self.edge_count,
            "is_prunable": self.is_prunable,
        }


@dataclass
class EntropyMetrics:
    """Entropy metrics for a graph or system."""

    metrics_id: str = field(default_factory=lambda: str(uuid4()))
    total_nodes: int = 0
    average_entropy: float = 0.0
    max_entropy: float = 0.0
    min_entropy: float = 0.0
    high_entropy_nodes: list[str] = field(default_factory=list)
    low_entropy_nodes: list[str] = field(default_factory=list)
    prunable_count: int = 0
    measured_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "metrics_id": self.metrics_id,
            "total_nodes": self.total_nodes,
            "average_entropy": self.average_entropy,
            "max_entropy": self.max_entropy,
            "min_entropy": self.min_entropy,
            "high_entropy_nodes": self.high_entropy_nodes[:5],
            "low_entropy_nodes": self.low_entropy_nodes[:5],
            "prunable_count": self.prunable_count,
            "measured_at": self.measured_at.isoformat(),
        }


@dataclass
class RenyiEntropyResult:
    """Result of Renyi entropy calculation."""

    entropy: float = 0.0
    alpha: float = 2.0
    special_case: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "entropy": self.entropy,
            "alpha": self.alpha,
            "special_case": self.special_case,
        }


@dataclass
class KLDivergenceResult:
    """Result of KL divergence calculation."""

    divergence: float = 0.0
    is_finite: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "divergence": self.divergence,
            "is_finite": self.is_finite,
        }


def renyi_entropy(probabilities: list[float], alpha: float = 2.0) -> float:
    """Calculate Renyi entropy of order alpha.

    H_alpha(X) = 1/(1-alpha) * log2(sum(p_i^alpha))

    Special cases:
    - alpha -> 0: Hartley entropy = log2(|support|)
    - alpha = 1: Shannon entropy (limit)
    - alpha = 2: Collision entropy
    - alpha -> inf: Min-entropy = -log2(max(p))
    """
    if not probabilities:
        return 0.0

    # Filter to positive probabilities
    probs = [p for p in probabilities if p > 0]
    if not probs:
        return 0.0

    # Hartley entropy: alpha -> 0
    if alpha <= 0:
        return math.log2(len(probs))

    # Shannon entropy: alpha = 1 (limit case)
    if abs(alpha - 1.0) < 1e-10:
        return -sum(p * math.log2(p) for p in probs)

    # Min-entropy: alpha -> infinity
    if alpha > 1e6:
        return -math.log2(max(probs))

    # General Renyi entropy
    power_sum = sum(p**alpha for p in probs)
    if power_sum <= 0:
        return 0.0
    return math.log2(power_sum) / (1 - alpha)


def kl_divergence(p: list[float], q: list[float]) -> float:
    """Calculate KL divergence D_KL(P || Q).

    D_KL(P || Q) = sum(P(x) * log2(P(x) / Q(x)))

    Returns inf when absolute continuity is violated (Q(x)=0 where P(x)>0).
    """
    if len(p) != len(q):
        raise ValueError(f"Distributions must have same length: {len(p)} vs {len(q)}")

    divergence = 0.0
    for pi, qi in zip(p, q, strict=True):
        if pi > 0:
            if qi <= 0:
                return float("inf")
            divergence += pi * math.log2(pi / qi)
    return divergence


def beta_kl_divergence(alpha1: float, beta1: float, alpha2: float, beta2: float) -> float:
    """KL divergence between two Beta distributions using log-gamma.

    D_KL(Beta(a1,b1) || Beta(a2,b2)) =
        ln B(a2,b2) - ln B(a1,b1)
        + (a1-a2)*psi(a1) + (b1-b2)*psi(b1)
        + (a2-b2+b2-a1+a1-b1)*psi(a1+b1)

    Uses finite differences of lgamma to approximate the digamma function.
    """

    # ln B(a,b) = lgamma(a) + lgamma(b) - lgamma(a+b)
    def log_beta(a: float, b: float) -> float:
        return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)

    # Approximate digamma via finite difference: psi(x) ~ lgamma(x+h) - lgamma(x) / h
    h = 1e-8

    def digamma(x: float) -> float:
        return (math.lgamma(x + h) - math.lgamma(x)) / h

    lb1 = log_beta(alpha1, beta1)
    lb2 = log_beta(alpha2, beta2)

    psi_a1 = digamma(alpha1)
    psi_b1 = digamma(beta1)
    psi_ab1 = digamma(alpha1 + beta1)

    return (
        lb2
        - lb1
        + (alpha1 - alpha2) * psi_a1
        + (beta1 - beta2) * psi_b1
        + (alpha2 + beta2 - alpha1 - beta1) * psi_ab1
    )


class InformationTheoryService:
    """Service for information-theoretic analysis.

    H(X) = -sum(p(x) * log2(p(x)))
    Higher entropy = more informative.
    """

    def calculate_shannon_entropy(self, probabilities: list[float]) -> float:
        if not probabilities:
            return 0.0
        entropy_val = 0.0
        for p in probabilities:
            if p > 0:
                entropy_val -= p * math.log2(p)
        return entropy_val

    def calculate_node_entropy(
        self,
        node_id: str,
        edge_weights: list[float],
        node_name: str = "",
    ) -> NodeEntropy:
        if not edge_weights:
            return NodeEntropy(
                node_id=node_id,
                node_name=node_name,
                entropy=0.0,
                edge_count=0,
                is_prunable=True,
            )

        total = sum(edge_weights)
        if total <= 0:
            return NodeEntropy(
                node_id=node_id,
                node_name=node_name,
                entropy=0.0,
                edge_count=len(edge_weights),
                is_prunable=True,
            )

        probabilities = [w / total for w in edge_weights]
        ent = self.calculate_shannon_entropy(probabilities)
        threshold = get_constant("ENTROPY_PRUNING_THRESHOLD")

        return NodeEntropy(
            node_id=node_id,
            node_name=node_name,
            entropy=ent,
            edge_count=len(edge_weights),
            edge_distribution=probabilities,
            is_prunable=ent < threshold,
        )

    def analyze_graph_entropy(
        self,
        nodes: list[dict[str, Any]],
    ) -> EntropyMetrics:
        if not nodes:
            return EntropyMetrics()

        entropies = []
        prunable_count = 0
        node_entropies: list[tuple[str, float]] = []

        for node in nodes:
            node_id = node.get("id", "")
            node_name = node.get("name", "")
            edge_weights = node.get("edge_weights", [])

            ne = self.calculate_node_entropy(node_id, edge_weights, node_name)
            entropies.append(ne.entropy)
            node_entropies.append((node_id, ne.entropy))

            if ne.is_prunable:
                prunable_count += 1

        node_entropies.sort(key=lambda x: x[1], reverse=True)

        return EntropyMetrics(
            total_nodes=len(nodes),
            average_entropy=sum(entropies) / len(entropies) if entropies else 0.0,
            max_entropy=max(entropies) if entropies else 0.0,
            min_entropy=min(entropies) if entropies else 0.0,
            high_entropy_nodes=[nid for nid, _ in node_entropies[:10]],
            low_entropy_nodes=[nid for nid, _ in node_entropies[-10:]],
            prunable_count=prunable_count,
        )

    def calculate_mutual_information(
        self,
        joint_probs: list[list[float]],
        marginal_x: list[float],
        marginal_y: list[float],
    ) -> float:
        mi = 0.0
        for i, px in enumerate(marginal_x):
            for j, py in enumerate(marginal_y):
                if i < len(joint_probs) and j < len(joint_probs[i]):
                    pxy = joint_probs[i][j]
                    if pxy > 0 and px > 0 and py > 0:
                        mi += pxy * math.log2(pxy / (px * py))
        return mi

    def calculate_information_gain(
        self,
        prior_entropy: float,
        posterior_entropy: float,
    ) -> float:
        return prior_entropy - posterior_entropy

    def suggest_pruning(
        self,
        nodes: list[dict[str, Any]],
        max_prunable_ratio: float = 0.1,
    ) -> list[str]:
        threshold = get_constant("ENTROPY_PRUNING_THRESHOLD")
        prunable = []
        for node in nodes:
            edge_weights = node.get("edge_weights", [])
            ne = self.calculate_node_entropy(node.get("id", ""), edge_weights)
            if ne.entropy < threshold:
                prunable.append((node.get("id", ""), ne.entropy))

        prunable.sort(key=lambda x: x[1])
        max_prune = int(len(nodes) * max_prunable_ratio)
        return [nid for nid, _ in prunable[:max_prune]]

    def calculate_renyi_entropy(
        self,
        probabilities: list[float],
        alpha: float = 2.0,
    ) -> RenyiEntropyResult:
        """Calculate Renyi entropy and classify the special case."""
        ent = renyi_entropy(probabilities, alpha)

        special_case = ""
        if alpha <= 0:
            special_case = "hartley"
        elif abs(alpha - 1.0) < 1e-10:
            special_case = "shannon"
        elif abs(alpha - 2.0) < 1e-10:
            special_case = "collision"
        elif alpha > 1e6:
            special_case = "min_entropy"

        return RenyiEntropyResult(entropy=ent, alpha=alpha, special_case=special_case)

    def calculate_kl_divergence(
        self,
        p: list[float],
        q: list[float],
    ) -> KLDivergenceResult:
        """Calculate KL divergence between two distributions."""
        div = kl_divergence(p, q)
        return KLDivergenceResult(
            divergence=div,
            is_finite=not math.isinf(div),
        )


def entropy(probabilities: list[float]) -> float:
    """Calculate Shannon entropy."""
    return InformationTheoryService().calculate_shannon_entropy(probabilities)


def binary_entropy(p: float) -> float:
    """Calculate entropy of a binary variable."""
    if p <= 0 or p >= 1:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)
