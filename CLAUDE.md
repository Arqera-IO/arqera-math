# Claude Memory — arqera-math

Mathematical foundations library powering the Aqera ecosystem.

## Architecture

**Pure Python 3.11+ library. Zero runtime dependencies.**

### Source Modules (`src/arqera_math/`)
| Module | Purpose |
|--------|---------|
| `bayesian.py` | Beta-binomial trust model (BayesianTrustService) — posterior updates, credible intervals, evidence weighting |
| `graph_analysis.py` | PageRank, centrality metrics, clustering coefficients |
| `information_theory.py` | Shannon entropy, pruning algorithms, information gain |
| `constants.py` | 27 tuned mathematical constants with bounds validation |
| `__init__.py` | Public API — 40 exports in `__all__` |

### Tests (`tests/`)
| Test | Covers |
|------|--------|
| `test_bayesian.py` | Trust updates, evidence accumulation, interval computation |
| `test_graph_analysis.py` | PageRank convergence, centrality, graph metrics |
| `test_constants.py` | All 27 constants exist, within bounds, correct types |

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

## Definition of Done

A change is complete when:
1. `ruff check src/` passes clean
2. `pytest tests/ -v` — all tests pass
3. All 40 items in `__all__` export correctly
4. All 27 constants remain within bounds
5. No external dependencies introduced
6. Downstream compatibility: digital-twin still passes its tests

## Downstream Consumers

- **digital-twin** (`~/Desktop/Project/digital-twin`) — Uses Bayesian trust, PageRank, entropy
- Any change here must be verified against downstream consumers

## Git Protocol

- Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
- Commit messages: `feat:`, `fix:`, `refactor:`, `test:`, `docs:` prefixes
