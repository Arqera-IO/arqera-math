"""ARQERA Mathematical Foundations.

Extracted from ARQERA's engine for reuse across projects:
- Bayesian Inference (Beta-binomial trust model)
- Graph Analysis (PageRank, centrality, clustering)
- Information Theory (Shannon entropy, pruning)
- Constants Registry (tuned mathematical constants)
- Decision Theory (weighted scoring, sensitivity analysis)
- Temporal Dynamics (trust forecasting, anomaly detection, trend analysis)
- Multi-Objective Optimization (Pareto frontier, dominance, weighted sum)
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
from arqera_math.decision_theory import (
    DecisionCriterion,
    DecisionMatrix,
    DecisionOption,
    DecisionResult,
    decision_rank,
    weighted_score,
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
from arqera_math.multi_objective import (
    ObjectiveWeight,
    ParetoPoint,
    ParetoResult,
    dominates,
    pareto_frontier,
    weighted_sum,
)
from arqera_math.temporal_dynamics import (
    TrendAnalysis,
    TrendPoint,
    TrustForecast,
    detect_anomaly,
    forecast_trust,
    linear_trend,
)

__all__ = [
    # Bayesian
    "BayesianTrustService",
    "BeliefState",
    "TrustUpdate",
    "bayesian_update",
    "trust_from_evidence",
    # Constants
    "MATH_CONSTANTS",
    "ConstantDomain",
    "MathConstant",
    "get_constant",
    "get_constant_info",
    "list_constants_by_domain",
    "validate_constant_update",
    # Decision Theory
    "DecisionCriterion",
    "DecisionMatrix",
    "DecisionOption",
    "DecisionResult",
    "decision_rank",
    "weighted_score",
    # Graph Analysis
    "CentralityMetrics",
    "GraphAnalysisService",
    "NodeImportance",
    "find_hubs_and_authorities",
    "simple_pagerank",
    # Information Theory
    "EntropyMetrics",
    "InformationTheoryService",
    "NodeEntropy",
    "binary_entropy",
    "entropy",
    # Multi-Objective
    "ObjectiveWeight",
    "ParetoPoint",
    "ParetoResult",
    "dominates",
    "pareto_frontier",
    "weighted_sum",
    # Temporal Dynamics
    "TrendAnalysis",
    "TrendPoint",
    "TrustForecast",
    "detect_anomaly",
    "forecast_trust",
    "linear_trend",
]
