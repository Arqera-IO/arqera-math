# arqera-math

[![CI](https://github.com/Arqera-IO/arqera-math/actions/workflows/ci.yaml/badge.svg)](https://github.com/Arqera-IO/arqera-math/actions/workflows/ci.yaml)
[![PyPI](https://img.shields.io/pypi/v/arqera-math.svg)](https://pypi.org/project/arqera-math/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**Mathematical foundations for AI governance.** 9 algorithms, 14 modules, 74 exports, 27 tuned constants. Pure Python. Zero dependencies.

Built by [ARQERA](https://arqera.io) for production AI systems that need trust scoring, decision analysis, and self-organizing behaviour.

---

## Why arqera-math?

Most AI governance libraries depend on NumPy, SciPy, or TensorFlow. arqera-math is different:

- **Zero dependencies.** Pure Python stdlib. No binary wheels. No version conflicts. Runs anywhere Python runs.
- **Typed dataclasses everywhere.** Every return value is a `@dataclass` with full type annotations. No raw dicts.
- **Deterministic.** No randomness without explicit seeds. Every function is reproducible.
- **Self-contained modules.** Each module covers one mathematical domain. No circular imports.
- **Tested.** 105 tests covering 100% of the public API.

## Install

```bash
pip install arqera-math
```

Requires Python 3.11+. No dependencies to install -- it is pure stdlib Python.

## Quick Start

### Bayesian Trust Scoring

Track trust in an entity using Beta-binomial conjugate priors. Each piece of evidence updates the posterior.

```python
from arqera_math import BayesianTrustService

service = BayesianTrustService()

# Create a belief with uniform prior
belief = service.create_belief("agent-1", prior_trust=0.5)
print(f"Initial trust: {belief.mean:.3f}")  # 0.500

# Positive evidence increases trust
update = service.update_trust("agent-1", positive_evidence=3)
print(f"After 3 positive: {update.posterior_mean:.3f}")  # ~0.615

# Negative evidence decreases trust
update = service.update_trust("agent-1", negative_evidence=2)
print(f"After 2 negative: {update.posterior_mean:.3f}")  # ~0.533

# Credible interval
lower, upper = service.compute_credible_interval(belief.alpha, belief.beta)
print(f"95% CI: [{lower:.3f}, {upper:.3f}]")

# Or use the standalone utility for quick calculations
from arqera_math import trust_from_evidence
score = trust_from_evidence(positive=8, negative=2)
print(f"Trust from evidence: {score:.3f}")  # ~0.650
```

### PageRank and Graph Analysis

Compute node importance in directed graphs using iterative PageRank.

```python
from arqera_math import simple_pagerank

# Adjacency list: node -> list of nodes it points to
graph = {
    "A": ["B", "C"],
    "B": ["C"],
    "C": ["A"],
    "D": ["C"],
}

ranks = simple_pagerank(graph, damping=0.85, iterations=100)
for node, rank in sorted(ranks.items(), key=lambda x: -x[1]):
    print(f"  {node}: {rank:.4f}")
```

### Information Theory

Measure uncertainty, divergence, and information content.

```python
from arqera_math import entropy, kl_divergence

# Shannon entropy of a probability distribution
h = entropy([0.5, 0.3, 0.2])
print(f"Shannon entropy: {h:.4f} bits")

# KL divergence between two distributions
d = kl_divergence([0.5, 0.3, 0.2], [0.33, 0.33, 0.34])
print(f"KL divergence: {d:.4f}")
```

### Physarum / Stigmergy Dynamics

Pheromone-based route optimization. Successful paths get reinforced, unused paths decay.

```python
from arqera_math import update_pheromone, pheromone_gradient

# Trail intensities (higher = more reinforced)
trails = {"route-A": 0.8, "route-B": 0.3, "route-C": 0.1}

# Reinforce a successful route: tau(t+1) = (1 - rho) * tau(t) + deposit
trails["route-A"] = update_pheromone(trails["route-A"], deposit=0.2, evaporation_rate=0.05)
print(f"Route A after reinforcement: {trails['route-A']:.3f}")  # 0.960

# Get gradient -- sorted strongest to weakest
gradient = pheromone_gradient(trails)
for name, intensity in gradient:
    print(f"  {name}: {intensity:.3f}")
```

### Decision Theory

Score options across multiple weighted criteria.

```python
from arqera_math import decision_rank

criteria = [
    {"name": "accuracy", "weight": 0.5},
    {"name": "latency", "weight": 0.3, "minimize": True},
    {"name": "cost", "weight": 0.2, "minimize": True},
]

options = [
    {"name": "model-A", "scores": {"accuracy": 0.95, "latency": 120, "cost": 50}},
    {"name": "model-B", "scores": {"accuracy": 0.88, "latency": 30, "cost": 10}},
    {"name": "model-C", "scores": {"accuracy": 0.92, "latency": 60, "cost": 25}},
]

ranked = decision_rank(criteria, options)
for result in ranked:
    print(f"  #{result['rank']}: {result['option_name']} (score: {result['weighted_score']:.3f})")
```

## Algorithms

| Module | What it does |
|--------|-------------|
| **Bayesian Inference** | Beta-binomial trust model with Fisher information and Cramer-Rao bounds |
| **Graph Analysis** | PageRank, degree/betweenness centrality, clustering coefficients, HITS |
| **Information Theory** | Shannon entropy, Renyi entropy, KL divergence, Beta-KL divergence |
| **Decision Theory** | Weighted multi-criteria decision matrices with sensitivity analysis |
| **Multi-Objective Optimization** | Pareto frontier extraction, dominance checking, weighted sum scalarization |
| **Stigmergy** | Pheromone-based route optimization (ant colony style) |
| **Quorum Sensing** | Hill function biological threshold curves for collective activation |
| **Stability Analysis** | Lyapunov functions and convergence verification |
| **Temporal Dynamics** | Trust forecasting, anomaly detection, linear trend analysis |

Plus: control theory (PID controllers), game theory (resource auctions), queueing theory (M/M/1, M/M/c), preconditions (demographic-informed Bayesian priors), and a constants registry with bounds validation.

## All Exports

The library exports 74 public symbols across 14 modules. Everything is importable directly from `arqera_math`:

```python
import arqera_math
print(len(arqera_math.__all__))  # 74
```

**Bayesian**: `BayesianTrustService`, `BeliefState`, `TrustUpdate`, `FisherInformationResult`, `bayesian_update`, `trust_from_evidence`, `fisher_information`, `cramer_rao_bound`

**Graph Analysis**: `GraphAnalysisService`, `CentralityMetrics`, `NodeImportance`, `simple_pagerank`, `find_hubs_and_authorities`

**Information Theory**: `InformationTheoryService`, `EntropyMetrics`, `NodeEntropy`, `KLDivergenceResult`, `RenyiEntropyResult`, `entropy`, `binary_entropy`, `kl_divergence`, `renyi_entropy`, `beta_kl_divergence`

**Decision Theory**: `DecisionMatrix`, `DecisionCriterion`, `DecisionOption`, `DecisionResult`, `decision_rank`, `weighted_score`

**Multi-Objective**: `ParetoResult`, `ParetoPoint`, `ObjectiveWeight`, `pareto_frontier`, `dominates`, `weighted_sum`

**Stigmergy**: `StigmergyService`, `PheromoneTrail`, `StigmergyMetrics`, `update_pheromone`, `pheromone_gradient`

**Quorum Sensing**: `QuorumSensingService`, `QuorumResponse`, `hill_function`

**Stability**: `StabilityService`, `StabilityAnalysis`, `lyapunov_function`, `check_stability`

**Temporal Dynamics**: `TrustForecast`, `TrendAnalysis`, `TrendPoint`, `forecast_trust`, `detect_anomaly`, `linear_trend`

**Control Theory**: `PIDController`, `ControllerState`, `ControlAction`, `simple_pid_step`

**Game Theory**: `ResourceAuction`, `ResourceClaim`, `AuctionResult`, `create_claim`

**Queueing**: `QueueingService`, `AgentQueue`, `QueueMetrics`

**Preconditions**: `PreconditionProfile`, `compute_domain_priors`, `compute_entity_prior`

**Constants**: `MATH_CONSTANTS`, `ConstantDomain`, `MathConstant`, `get_constant`, `get_constant_info`, `list_constants_by_domain`, `validate_constant_update`

## Constants

27 tuned mathematical constants across 12 domains, each with bounds validation:

```python
from arqera_math import get_constant, list_constants_by_domain, ConstantDomain

# Get a specific constant
value = get_constant("CONDUCTANCE_REINFORCEMENT")
print(value)  # 0.3

# List constants by domain
entropy_constants = list_constants_by_domain(ConstantDomain.ENTROPY)
for c in entropy_constants:
    print(f"  {c.name} = {c.value} (range: {c.min_value}..{c.max_value})")
```

## Used by ARQERA

arqera-math powers the mathematical engine behind [ARQERA](https://arqera.io), an AI operations platform for enterprise governance, trust scoring, and autonomous decision-making.

Every algorithm in this library is battle-tested in production: Bayesian trust updates run on live agent evaluations, PageRank scores real dependency graphs, and Physarum dynamics route actual AI workloads.

## Development

```bash
# Clone
git clone https://github.com/Arqera-IO/arqera-math.git
cd arqera-math

# Install with dev dependencies
pip install -e ".[dev]"

# Lint
ruff check src/

# Test
pytest tests/ -v

# Quality gate (must pass before commit)
ruff check src/ && pytest tests/ -v
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full contributor guidelines.

## License

Apache-2.0. See [LICENSE](LICENSE).

Copyright 2026 ARQERA Ltd.
