"""Tests for Graph Analysis Service."""

from arqera_math import GraphAnalysisService, find_hubs_and_authorities, simple_pagerank


def test_pagerank_simple():
    adj = {"A": ["B", "C"], "B": ["C"], "C": ["A"]}
    pr = simple_pagerank(adj, iterations=50)
    assert len(pr) == 3
    assert all(v > 0 for v in pr.values())
    # Sum should be approximately 1
    assert abs(sum(pr.values()) - 1.0) < 0.01


def test_pagerank_empty():
    svc = GraphAnalysisService()
    assert svc.compute_pagerank({}) == {}


def test_degree_centrality():
    svc = GraphAnalysisService()
    adj = {"A": ["B", "C"], "B": ["C"], "C": []}
    centrality = svc.compute_degree_centrality(adj)
    assert len(centrality) == 3
    # C has highest in-degree (2 incoming)
    assert centrality["C"] >= centrality["A"]


def test_clustering_coefficient():
    svc = GraphAnalysisService()
    # Triangle: A→B, B→C, C→A (full clustering)
    adj = {"A": ["B"], "B": ["C"], "C": ["A"]}
    clustering = svc.compute_clustering_coefficient(adj)
    assert all(v == 1.0 for v in clustering.values())


def test_analyze_graph():
    svc = GraphAnalysisService()
    adj = {"A": ["B", "C"], "B": ["C"], "C": ["A"]}
    metrics = svc.analyze_graph(adj)
    assert metrics.total_nodes == 3
    assert metrics.total_edges == 4
    assert metrics.graph_density > 0


def test_find_hubs_and_authorities():
    adj = {"A": ["B", "C", "D"], "B": [], "C": [], "D": []}
    hubs, authorities = find_hubs_and_authorities(adj)
    assert hubs[0] == "A"  # A has highest out-degree
