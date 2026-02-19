"""ARQERA Mathematical Foundations.

Extracted from ARQERA's engine for reuse across projects:
- Bayesian Inference (Beta-binomial trust model, Fisher information)
- Graph Analysis (PageRank, centrality, clustering)
- Information Theory (Shannon entropy, Renyi entropy, KL divergence, pruning)
- Constants Registry (tuned mathematical constants)
- Control Theory (PID controllers, self-healing feedback loops)
- Decision Theory (weighted scoring, sensitivity analysis)
- Game Theory (resource auctions, conflict resolution)
- Temporal Dynamics (trust forecasting, anomaly detection, trend analysis)
- Multi-Objective Optimization (Pareto frontier, dominance, weighted sum)
- Queueing Theory (M/M/1, M/M/c queue analysis)
- Stigmergy (pheromone-based route optimization)
- Quorum Sensing (biological threshold functions)
- Lyapunov Stability (convergence verification)
"""

from arqera_math.bayesian import (
    BayesianTrustService,
    BeliefState,
    FisherInformationResult,
    TrustUpdate,
    bayesian_update,
    cramer_rao_bound,
    fisher_information,
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
from arqera_math.control_theory import (
    ControlAction,
    ControllerState,
    PIDController,
    simple_pid_step,
)
from arqera_math.decision_theory import (
    DecisionCriterion,
    DecisionMatrix,
    DecisionOption,
    DecisionResult,
    decision_rank,
    weighted_score,
)
from arqera_math.game_theory import (
    AuctionResult,
    ResourceAuction,
    ResourceClaim,
    create_claim,
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
    KLDivergenceResult,
    NodeEntropy,
    RenyiEntropyResult,
    beta_kl_divergence,
    binary_entropy,
    entropy,
    kl_divergence,
    renyi_entropy,
)
from arqera_math.multi_objective import (
    ObjectiveWeight,
    ParetoPoint,
    ParetoResult,
    dominates,
    pareto_frontier,
    weighted_sum,
)
from arqera_math.preconditions import (
    PreconditionProfile,
    compute_domain_priors,
    compute_entity_prior,
)
from arqera_math.queueing import (
    AgentQueue,
    QueueingService,
    QueueMetrics,
)
from arqera_math.quorum_sensing import (
    QuorumResponse,
    QuorumSensingService,
    hill_function,
)
from arqera_math.stability import (
    StabilityAnalysis,
    StabilityService,
    check_stability,
    lyapunov_function,
)
from arqera_math.stigmergy import (
    PheromoneTrail,
    StigmergyMetrics,
    StigmergyService,
    pheromone_gradient,
    update_pheromone,
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
    "FisherInformationResult",
    "TrustUpdate",
    "bayesian_update",
    "cramer_rao_bound",
    "fisher_information",
    "trust_from_evidence",
    # Constants
    "MATH_CONSTANTS",
    "ConstantDomain",
    "MathConstant",
    "get_constant",
    "get_constant_info",
    "list_constants_by_domain",
    "validate_constant_update",
    # Control Theory
    "ControlAction",
    "ControllerState",
    "PIDController",
    "simple_pid_step",
    # Decision Theory
    "DecisionCriterion",
    "DecisionMatrix",
    "DecisionOption",
    "DecisionResult",
    "decision_rank",
    "weighted_score",
    # Game Theory
    "AuctionResult",
    "ResourceAuction",
    "ResourceClaim",
    "create_claim",
    # Graph Analysis
    "CentralityMetrics",
    "GraphAnalysisService",
    "NodeImportance",
    "find_hubs_and_authorities",
    "simple_pagerank",
    # Information Theory
    "EntropyMetrics",
    "InformationTheoryService",
    "KLDivergenceResult",
    "NodeEntropy",
    "RenyiEntropyResult",
    "beta_kl_divergence",
    "binary_entropy",
    "entropy",
    "kl_divergence",
    "renyi_entropy",
    # Multi-Objective
    "ObjectiveWeight",
    "ParetoPoint",
    "ParetoResult",
    "dominates",
    "pareto_frontier",
    "weighted_sum",
    # Preconditions
    "PreconditionProfile",
    "compute_domain_priors",
    "compute_entity_prior",
    # Quorum Sensing
    "QuorumResponse",
    "QuorumSensingService",
    "hill_function",
    # Queueing Theory
    "AgentQueue",
    "QueueingService",
    "QueueMetrics",
    # Stability
    "StabilityAnalysis",
    "StabilityService",
    "check_stability",
    "lyapunov_function",
    # Stigmergy
    "PheromoneTrail",
    "StigmergyMetrics",
    "StigmergyService",
    "pheromone_gradient",
    "update_pheromone",
    # Temporal Dynamics
    "TrendAnalysis",
    "TrendPoint",
    "TrustForecast",
    "detect_anomaly",
    "forecast_trust",
    "linear_trend",
]
