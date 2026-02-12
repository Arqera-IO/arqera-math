"""Tests for Constants Registry."""

import pytest

from arqera_math import (
    MATH_CONSTANTS,
    ConstantDomain,
    get_constant,
    get_constant_info,
    list_constants_by_domain,
    validate_constant_update,
)


def test_get_constant():
    assert get_constant("PAGERANK_DAMPING") == 0.85
    assert get_constant("BAYESIAN_PRIOR_STRENGTH") == 10.0


def test_get_constant_missing():
    with pytest.raises(KeyError):
        get_constant("NONEXISTENT")


def test_get_constant_info():
    info = get_constant_info("PAGERANK_DAMPING")
    assert info.name == "PAGERANK_DAMPING"
    assert info.domain == ConstantDomain.GRAPH


def test_list_constants_by_domain():
    graph_constants = list_constants_by_domain(ConstantDomain.GRAPH)
    assert len(graph_constants) >= 3
    names = {c.name for c in graph_constants}
    assert "PAGERANK_DAMPING" in names


def test_validate_constant_update():
    ok, msg = validate_constant_update("PAGERANK_DAMPING", 0.8)
    assert ok

    ok, msg = validate_constant_update("PAGERANK_DAMPING", 0.1)
    assert not ok


def test_all_constants_have_valid_domains():
    for name, const in MATH_CONSTANTS.items():
        assert isinstance(const.domain, ConstantDomain), f"{name} has invalid domain"
        assert const.value is not None, f"{name} has no value"
