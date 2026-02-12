"""Graph Analysis Service.

Provides graph-theoretic analysis:
- PageRank for node importance
- Centrality measures (degree, closeness)
- Clustering coefficient
- Hub/authority detection

Standalone — no SQLAlchemy or external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from arqera_math.constants import get_constant


@dataclass
class NodeImportance:
    """Importance scores for a graph node."""

    node_id: str
    node_name: str = ""
    pagerank: float = 0.0
    closeness_centrality: float = 0.0
    betweenness_centrality: float = 0.0
    degree_centrality: float = 0.0
    clustering_coefficient: float = 0.0
    in_degree: int = 0
    out_degree: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_name": self.node_name,
            "pagerank": self.pagerank,
            "degree_centrality": self.degree_centrality,
            "clustering_coefficient": self.clustering_coefficient,
            "in_degree": self.in_degree,
            "out_degree": self.out_degree,
        }


@dataclass
class CentralityMetrics:
    """Centrality metrics for a graph."""

    metrics_id: str = field(default_factory=lambda: str(uuid4()))
    total_nodes: int = 0
    total_edges: int = 0
    average_pagerank: float = 0.0
    average_clustering: float = 0.0
    graph_density: float = 0.0
    top_nodes_by_pagerank: list[str] = field(default_factory=list)
    top_nodes_by_centrality: list[str] = field(default_factory=list)
    hub_nodes: list[str] = field(default_factory=list)
    authority_nodes: list[str] = field(default_factory=list)
    measured_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "metrics_id": self.metrics_id,
            "total_nodes": self.total_nodes,
            "total_edges": self.total_edges,
            "average_pagerank": self.average_pagerank,
            "average_clustering": self.average_clustering,
            "graph_density": self.graph_density,
            "top_nodes_by_pagerank": self.top_nodes_by_pagerank[:5],
            "top_nodes_by_centrality": self.top_nodes_by_centrality[:5],
            "measured_at": self.measured_at.isoformat(),
        }


class GraphAnalysisService:
    """Service for graph-theoretic analysis.

    PageRank: PR(p) = (1-d)/n + d * sum(PR(t)/L(t))
    """

    def compute_pagerank(
        self,
        adjacency: dict[str, list[str]],
        damping: float | None = None,
        max_iterations: int | None = None,
        tolerance: float | None = None,
    ) -> dict[str, float]:
        if damping is None:
            damping = get_constant("PAGERANK_DAMPING")
        if max_iterations is None:
            max_iterations = int(get_constant("PAGERANK_ITERATIONS"))
        if tolerance is None:
            tolerance = get_constant("PAGERANK_TOLERANCE")

        nodes = set(adjacency.keys())
        for targets in adjacency.values():
            nodes.update(targets)
        nodes_list = list(nodes)
        n = len(nodes_list)

        if n == 0:
            return {}

        initial_pr = 1.0 / n
        pr = dict.fromkeys(nodes_list, initial_pr)
        out_degree = {node: len(adjacency.get(node, [])) for node in nodes_list}

        for _ in range(max_iterations):
            new_pr = {}
            for node in nodes_list:
                incoming_sum = 0.0
                for source, targets in adjacency.items():
                    if node in targets and out_degree[source] > 0:
                        incoming_sum += pr[source] / out_degree[source]
                new_pr[node] = (1 - damping) / n + damping * incoming_sum

            max_diff = max(abs(new_pr[node] - pr[node]) for node in nodes_list)
            pr = new_pr
            if max_diff < tolerance:
                break

        return pr

    def compute_degree_centrality(
        self,
        adjacency: dict[str, list[str]],
    ) -> dict[str, float]:
        nodes = set(adjacency.keys())
        for targets in adjacency.values():
            nodes.update(targets)
        n = len(nodes)

        if n <= 1:
            return dict.fromkeys(nodes, 0.0)

        in_degree: dict[str, int] = dict.fromkeys(nodes, 0)
        out_degree: dict[str, int] = dict.fromkeys(nodes, 0)

        for source, targets in adjacency.items():
            out_degree[source] = len(targets)
            for target in targets:
                in_degree[target] = in_degree.get(target, 0) + 1

        centrality = {}
        for node in nodes:
            total_degree = in_degree[node] + out_degree[node]
            centrality[node] = total_degree / (2 * (n - 1))
        return centrality

    def compute_clustering_coefficient(
        self,
        adjacency: dict[str, list[str]],
    ) -> dict[str, float]:
        undirected: dict[str, set[str]] = {}
        for source, targets in adjacency.items():
            if source not in undirected:
                undirected[source] = set()
            for target in targets:
                undirected[source].add(target)
                if target not in undirected:
                    undirected[target] = set()
                undirected[target].add(source)

        clustering = {}
        for node, neighbors in undirected.items():
            k = len(neighbors)
            if k < 2:
                clustering[node] = 0.0
                continue

            edges_between = 0
            neighbors_list = list(neighbors)
            for i, n1 in enumerate(neighbors_list):
                for n2 in neighbors_list[i + 1 :]:
                    if n2 in undirected.get(n1, set()):
                        edges_between += 1

            max_edges = k * (k - 1) / 2
            clustering[node] = edges_between / max_edges if max_edges > 0 else 0.0

        return clustering

    def analyze_graph(
        self,
        adjacency: dict[str, list[str]],
        node_names: dict[str, str] | None = None,
    ) -> CentralityMetrics:
        node_names = node_names or {}

        pagerank = self.compute_pagerank(adjacency)
        degree_centrality = self.compute_degree_centrality(adjacency)
        clustering = self.compute_clustering_coefficient(adjacency)

        nodes = set(adjacency.keys())
        for targets in adjacency.values():
            nodes.update(targets)
        n = len(nodes)

        total_edges = sum(len(targets) for targets in adjacency.values())
        max_edges = n * (n - 1)
        density = total_edges / max_edges if max_edges > 0 else 0.0

        by_pagerank = sorted(nodes, key=lambda x: pagerank.get(x, 0), reverse=True)
        by_centrality = sorted(nodes, key=lambda x: degree_centrality.get(x, 0), reverse=True)

        return CentralityMetrics(
            total_nodes=n,
            total_edges=total_edges,
            average_pagerank=sum(pagerank.values()) / n if n > 0 else 0.0,
            average_clustering=sum(clustering.values()) / n if n > 0 else 0.0,
            graph_density=density,
            top_nodes_by_pagerank=by_pagerank[:10],
            top_nodes_by_centrality=by_centrality[:10],
        )

    def get_node_importance(
        self,
        node_id: str,
        adjacency: dict[str, list[str]],
        node_name: str = "",
    ) -> NodeImportance:
        pagerank = self.compute_pagerank(adjacency)
        degree_centrality = self.compute_degree_centrality(adjacency)
        clustering = self.compute_clustering_coefficient(adjacency)

        out_degree = len(adjacency.get(node_id, []))
        in_degree = sum(1 for targets in adjacency.values() if node_id in targets)

        return NodeImportance(
            node_id=node_id,
            node_name=node_name,
            pagerank=pagerank.get(node_id, 0.0),
            degree_centrality=degree_centrality.get(node_id, 0.0),
            clustering_coefficient=clustering.get(node_id, 0.0),
            in_degree=in_degree,
            out_degree=out_degree,
        )

    def find_critical_nodes(
        self,
        adjacency: dict[str, list[str]],
        top_n: int = 10,
    ) -> list[str]:
        pagerank = self.compute_pagerank(adjacency)
        sorted_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
        return [node for node, _ in sorted_nodes[:top_n]]


def simple_pagerank(
    adjacency: dict[str, list[str]],
    damping: float = 0.85,
    iterations: int = 20,
) -> dict[str, float]:
    """Simple PageRank computation."""
    return GraphAnalysisService().compute_pagerank(adjacency, damping, iterations)


def find_hubs_and_authorities(
    adjacency: dict[str, list[str]],
) -> tuple[list[str], list[str]]:
    """Find hub nodes (high out-degree) and authority nodes (high in-degree)."""
    nodes = set(adjacency.keys())
    for targets in adjacency.values():
        nodes.update(targets)

    out_degrees = {node: len(adjacency.get(node, [])) for node in nodes}
    in_degrees: dict[str, int] = dict.fromkeys(nodes, 0)
    for targets in adjacency.values():
        for target in targets:
            in_degrees[target] = in_degrees.get(target, 0) + 1

    hubs = sorted(nodes, key=lambda x: out_degrees.get(x, 0), reverse=True)[:5]
    authorities = sorted(nodes, key=lambda x: in_degrees.get(x, 0), reverse=True)[:5]
    return hubs, authorities
