# Contributing to arqera-math

Thank you for your interest in contributing. This guide covers everything you need to get started.

## Setup

```bash
# Clone and enter the project
git clone https://github.com/Arqera-IO/arqera-math.git
cd arqera-math

# Create virtual environment and install
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Or with [uv](https://docs.astral.sh/uv/) (faster):

```bash
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Development Workflow

### 1. Create a branch

```bash
git checkout -b feat/your-feature
```

### 2. Make your changes

Edit source files in `src/arqera_math/`. Add tests in `tests/`.

### 3. Lint

```bash
ruff check src/
```

### 4. Test

```bash
pytest tests/ -v
```

### 5. Quality gate (both must pass)

```bash
ruff check src/ && pytest tests/ -v
```

### 6. Commit and open a PR

Use conventional prefixes: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`

```bash
git commit -m "feat: add new algorithm for X"
```

## Key Rules

- **Zero external dependencies.** stdlib only. No NumPy, SciPy, or anything outside Python's standard library. This is a core design principle.
- **All public API** must be listed in `__all__` in `__init__.py`.
- **Type hints and docstrings** required on all public functions.
- **Return dataclasses**, not raw dicts. Every structured return value should be a `@dataclass` with type annotations.
- **Deterministic.** No randomness without explicit seeds. Every function must be reproducible.
- **Tests required.** Every new public function needs at least one test. All tests must be deterministic (no flaky tests).

## Code Style

- Line length: 100 characters
- Target: Python 3.11+
- Linter: [Ruff](https://docs.astral.sh/ruff/) with rules `E`, `F`, `I`, `W`, `UP`, `B`, `SIM`
- All `zip()` calls must use `strict=True` for dimension safety

## Project Structure

```
arqera-math/
  src/
    arqera_math/
      __init__.py        # Public API (74 exports in __all__)
      bayesian.py        # Beta-binomial trust model
      graph_analysis.py  # PageRank, centrality
      information_theory.py  # Entropy, KL divergence
      decision_theory.py     # Decision matrices
      multi_objective.py     # Pareto frontiers
      stigmergy.py           # Pheromone optimization
      quorum_sensing.py      # Hill function thresholds
      stability.py           # Lyapunov analysis
      temporal_dynamics.py   # Trend analysis, forecasting
      control_theory.py      # PID controllers
      game_theory.py         # Resource auctions
      queueing.py            # Queue analysis
      preconditions.py       # Bayesian priors
      constants.py           # 27 tuned constants
  tests/
    test_*.py            # One test file per module
```

## Adding a New Module

1. Create `src/arqera_math/your_module.py`
2. Define typed dataclasses for all return values
3. Export public symbols via `__all__` at module level
4. Import and re-export in `src/arqera_math/__init__.py`
5. Add the new symbols to `__init__.py`'s `__all__`
6. Create `tests/test_your_module.py` with full coverage
7. Run the quality gate: `ruff check src/ && pytest tests/ -v`

## Reporting Issues

Open an issue at [github.com/Arqera-IO/arqera-math/issues](https://github.com/Arqera-IO/arqera-math/issues) with:

- Python version (`python --version`)
- arqera-math version (`python -c "import arqera_math; print(arqera_math.__version__)"`)
- Minimal reproduction code
- Expected vs actual behaviour

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0, consistent with the project's [LICENSE](LICENSE).

See [CONVENTIONS.md](CONVENTIONS.md) for full engineering standards.
