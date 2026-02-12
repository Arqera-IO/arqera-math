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
                prunable.append((node.get("id"), ne.entropy))

        prunable.sort(key=lambda x: x[1])
        max_prune = int(len(nodes) * max_prunable_ratio)
        return [nid for nid, _ in prunable[:max_prune]]


def entropy(probabilities: list[float]) -> float:
    """Calculate Shannon entropy."""
    return InformationTheoryService().calculate_shannon_entropy(probabilities)


def binary_entropy(p: float) -> float:
    """Calculate entropy of a binary variable."""
    if p <= 0 or p >= 1:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)
