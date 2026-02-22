# arqera-math v0.1.0 -- Mathematical Foundations for AI Governance

The first public release of arqera-math, the mathematical engine behind [ARQERA](https://arqera.io).

## Highlights

- **14 modules** covering 9 algorithm families
- **74 public exports** -- all typed, all documented
- **27 tuned constants** across 12 domains, each with bounds validation
- **105 tests** -- 100% public API coverage
- **Zero dependencies** -- pure Python 3.11+ stdlib
- **Fully typed** -- `py.typed` marker, dataclass returns, type annotations throughout

## Modules

| Module | Exports | Description |
|--------|---------|-------------|
| Bayesian Inference | 8 | Beta-binomial trust model, Fisher information, Cramer-Rao bounds |
| Graph Analysis | 5 | PageRank, degree/betweenness centrality, clustering coefficients, HITS |
| Information Theory | 10 | Shannon entropy, Renyi entropy, KL divergence, Beta-KL divergence |
| Decision Theory | 6 | Weighted multi-criteria decision matrices with sensitivity analysis |
| Multi-Objective Optimization | 6 | Pareto frontier extraction, dominance checking, weighted sum scalarization |
| Stigmergy | 5 | Pheromone-based route optimization (ant colony style) |
| Quorum Sensing | 3 | Hill function biological threshold curves for collective activation |
| Stability Analysis | 4 | Lyapunov functions and convergence verification |
| Temporal Dynamics | 6 | Trust forecasting, anomaly detection, linear trend analysis |
| Control Theory | 4 | PID controllers with state management |
| Game Theory | 4 | Resource auctions and fair allocation |
| Queueing Theory | 3 | M/M/1 and M/M/c queue analysis |
| Preconditions | 3 | Demographic-informed Bayesian priors |
| Constants Registry | 7 | 27 tuned constants with bounds validation and domain grouping |

## Install

```bash
pip install arqera-math
```

## Quick Example

```python
from arqera_math import trust_from_evidence, simple_pagerank, entropy

# Bayesian trust from evidence
score = trust_from_evidence(positive=8, negative=2)

# PageRank on a directed graph
ranks = simple_pagerank({"A": ["B", "C"], "B": ["C"], "C": ["A"]})

# Shannon entropy of a distribution
h = entropy([0.5, 0.3, 0.2])
```

## What's Next

- v0.2.0: Additional distance metrics, correlation functions, and extended graph algorithms
- Community contributions welcome -- see [CONTRIBUTING.md](CONTRIBUTING.md)

## Links

- Repository: https://github.com/Arqera-IO/arqera-math
- Documentation: https://github.com/Arqera-IO/arqera-math#readme
- Issues: https://github.com/Arqera-IO/arqera-math/issues
- ARQERA Platform: https://arqera.io
