# Claude Memory — arqera-math

Mathematical foundations library powering the ARQERA ecosystem.

## Architecture

**Pure Python 3.11+ library. Zero runtime dependencies.**

### Source Modules (`src/arqera_math/`)
| Module | Purpose |
|--------|---------|
| `bayesian.py` | Beta-binomial trust model, Fisher information, Cramér-Rao bound |
| `graph_analysis.py` | PageRank, centrality metrics, clustering coefficients |
| `information_theory.py` | Shannon entropy, Rényi entropy, KL divergence, pruning |
| `decision_theory.py` | Decision matrices, weighted scoring, multi-criteria ranking |
| `control_theory.py` | PID controllers, control actions, state management |
| `game_theory.py` | Resource auctions, fair allocation, claims resolution |
| `multi_objective.py` | Pareto frontiers, dominance checks, weighted sums |
| `queueing.py` | Agent queues, service metrics, load balancing |
| `temporal_dynamics.py` | Trend analysis, anomaly detection, trust forecasting |
| `preconditions.py` | Demographic-informed Bayesian priors |
| `stigmergy.py` | Pheromone-based route optimization (ACO-style) |
| `quorum_sensing.py` | Hill function biological threshold curves |
| `stability.py` | Lyapunov stability analysis, convergence verification |
| `constants.py` | 27 tuned mathematical constants across 12 domains |
| `__init__.py` | Public API — 74 exports in `__all__` |

### Tests (`tests/`)
| Test | Covers |
|------|--------|
| `test_bayesian.py` | Trust updates, evidence accumulation, Fisher info, Cramér-Rao |
| `test_graph_analysis.py` | PageRank convergence, centrality, graph metrics |
| `test_constants.py` | All 27 constants exist, within bounds, correct types |
| `test_decision_theory.py` | Decision matrices, ranking, weighted scores |
| `test_multi_objective.py` | Pareto frontiers, dominance, weighted sums |
| `test_temporal_dynamics.py` | Trend detection, anomaly scoring, forecasting |
| `test_preconditions.py` | Demographic priors, domain mapping, entity priors |
| `test_information_theory.py` | Rényi entropy, KL divergence, Beta KL divergence |
| `test_stigmergy.py` | Pheromone deposit/evaporate, gradient, bounds |
| `test_quorum_sensing.py` | Hill function, activation thresholds, batch eval |
| `test_stability.py` | Lyapunov function, convergence/divergence/oscillation |

## Commands

```bash
# Install
pip install -e .                    # Runtime only
pip install -e ".[dev]"             # With pytest, ruff

# Test
pytest tests/ -v                    # All tests
pytest tests/test_bayesian.py -v    # Specific module

# Lint
ruff check src/                     # Line length: 100, target: py311+
```

## Key Patterns

- All public functions are exported via `__all__` in `__init__.py`
- Constants are registered with bounds: `(name, value, min, max, description)`
- Bayesian updates use Beta(alpha, beta) conjugate prior
- Graph analysis returns typed dataclasses, not raw dicts
- No external dependencies — this library must remain self-contained
- All `zip()` calls use `strict=True` for dimension safety

## Definition of Done

A change is complete when:
1. `ruff check src/` passes clean
2. `pytest tests/ -v` — all tests pass
3. All 74 items in `__all__` export correctly
4. All 27 constants remain within bounds
5. No external dependencies introduced
6. Downstream compatibility: digital-twin still passes its tests

## Downstream Consumers

- **digital-twin** (`~/Desktop/Project/digital-twin`) — Uses Bayesian trust, PageRank, entropy
- **ARQERA** (`~/Desktop/Project/ARQERA`) — Backend gravity services use all math modules
- Any change here must be verified against downstream consumers

## MCP Dispatch

arqera-math is a pure library — fewer MCPs apply, but these do:

| Task | Tool | How |
|------|------|-----|
| Verify downstream impact | Bash | Run digital-twin tests after arqera-math changes |
| GPU-accelerated testing | SSH to homelab | `ssh dgx-spark` or `ssh pc-wsl` for heavy computation benchmarks |
| Research mathematical methods | WebSearch | Search for algorithms, papers, implementations |
| Document changes | Google Workspace MCP | Create design docs for mathematical modules |
| Track library metrics | PostHog MCP | Monitor download/usage metrics if published |
| CI/CD status | `gh` CLI | `gh run list --repo gashiru/arqera-math --limit 5` |

**After every arqera-math change:**
1. Run gate: `ruff check src/ && pytest tests/ -v`
2. Verify all 74 exports: `python -c "import arqera_math; print(len(arqera_math.__all__))"`
3. Run digital-twin tests: `cd ../digital-twin && pytest tests/ -v`

## Git Protocol

- Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
- Commit messages: `feat:`, `fix:`, `refactor:`, `test:`, `docs:` prefixes
