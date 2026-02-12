"""ARQERA Mathematical Foundations.

Extracted from ARQERA's engine for reuse across projects:
- Bayesian Inference (Beta-binomial trust model)
- Graph Analysis (PageRank, centrality, clustering)
- Information Theory (Shannon entropy, pruning)
- Constants Registry (tuned mathematical constants)
"""

from arqera_math.bayesian import (
    BayesianTrustService,
    BeliefState,
    TrustUpdate,
    bayesian_update,
    trust_from_evidence,
)
from arqera_math.constants import (
    MATH_CONSTANTS,
    ConstantDomain,
    MathConstant,
    get_constant,
    get_constant_info,
    list_constants_by_domain,
    validate_constant_update,
)
from arqera_math.graph_analysis import (
    CentralityMetrics,
    GraphAnalysisService,
    NodeImportance,
    find_hubs_and_authorities,
    simple_pagerank,
)
from arqera_math.information_theory import (
    EntropyMetrics,
    InformationTheoryService,
    NodeEntropy,
    binary_entropy,
    entropy,
)

__all__ = [
    "MATH_CONSTANTS",
    "BayesianTrustService",
    "BeliefState",
    "CentralityMetrics",
    "ConstantDomain",
    "EntropyMetrics",
    "GraphAnalysisService",
    "InformationTheoryService",
    "MathConstant",
    "NodeEntropy",
    "NodeImportance",
    "TrustUpdate",
    "bayesian_update",
    "binary_entropy",
    "entropy",
    "find_hubs_and_authorities",
    "get_constant",
    "get_constant_info",
    "list_constants_by_domain",
    "simple_pagerank",
    "trust_from_evidence",
    "validate_constant_update",
]
