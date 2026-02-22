# arqera-math — Engineering Conventions

## Project Overview

arqera-math is a **pure Python 3.11+ mathematical foundations library** with zero runtime dependencies. It provides Bayesian inference, graph analysis, information theory, decision theory, control theory, game theory, multi-objective optimization, queueing models, and temporal dynamics.

## Tech Stack

| Component | Tool | Notes |
|-----------|------|-------|
| Language | Python 3.11+ | Type hints required |
| Build | Hatchling | `pyproject.toml` config |
| Linter | Ruff | Line length 100, rules: E, F, I, W, UP, B, SIM |
| Tests | pytest + pytest-asyncio | `asyncio_mode = "strict"` |
| Package manager | uv (recommended) or pip | `uv pip install -e ".[dev]"` |
| Dependencies | **None** | Zero runtime dependencies. This is non-negotiable. |

## Quality Gate

Run before every commit:

```bash
ruff check src/ && pytest tests/ -v
```

Both must pass clean. No exceptions.

## Coding Standards

### Style

- **Line length**: 100 characters max
- **Imports**: Sorted by ruff (isort rules)
- **Type hints**: Required on all public functions
- **Docstrings**: Required on all public functions and classes
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_SNAKE` for constants

### Architecture Rules

- **No external dependencies**. stdlib only. If you need something, implement it.
- **Return typed dataclasses**, not raw dicts. Every structured return value gets a dataclass.
- **Functions are pure where possible**. Minimize side effects. No global state mutation.
- **Modules are self-contained**. Each module covers one mathematical domain.

## Key Patterns

### Exports

All public API surfaces are listed in `__init__.py` via `__all__`. When adding a new public function or class:

1. Define it in the appropriate module
2. Add it to `__all__` in `__init__.py`
3. Verify the export count: `python -c "import arqera_math; print(len(arqera_math.__all__))"`

### Constants

Constants are registered with bounds validation: `(name, value, min, max, description)`. Every constant must have:

- A meaningful name
- A valid numeric value
- Min/max bounds that the value falls within
- A human-readable description

### Bayesian Updates

The trust model uses Beta-binomial conjugate priors. Beta(alpha, beta) distributions are updated with evidence. Credible intervals are computed from the posterior.

### Dataclasses

All structured return types use `@dataclass` with type annotations. No `TypedDict`, no raw dicts for structured data.

## Testing

### Running Tests

```bash
# All tests
pytest tests/ -v

# Single module
pytest tests/test_bayesian.py -v

# With coverage (if installed)
pytest tests/ -v --cov=arqera_math
```

### Test Standards

- **Deterministic**: No randomness without fixed seeds. No network calls.
- **Fast**: Each test file should run in under 2 seconds.
- **Behavioral**: Test what the function does, not how it does it.
- **Named clearly**: `test_<function>_<scenario>_<expected>` pattern.
- **One assertion focus**: Each test should verify one behavior.

### What to Test

- All public functions (everything in `__all__`)
- Edge cases: empty inputs, zero values, boundary conditions
- Constants: existence, type, bounds compliance
- Mathematical properties: convergence, monotonicity, symmetry where expected

## Definition of Done

A change is complete when:

1. `ruff check src/` passes clean
2. `pytest tests/ -v` — all tests pass
3. All items in `__all__` export correctly
4. All constants remain within their declared bounds
5. No external dependencies introduced
6. New public functions have type hints and docstrings
7. New functionality has corresponding tests

## Git Protocol

### Commit Messages

Use conventional prefixes:

- `feat:` — New functionality
- `fix:` — Bug fix
- `refactor:` — Code restructure without behavior change
- `test:` — Test additions or changes
- `docs:` — Documentation only

### Co-Author

All AI-assisted commits include:

```
Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

### Pre-Commit Checklist

1. Run `ruff check src/`
2. Run `pytest tests/ -v`
3. Verify exports if `__init__.py` changed
4. Verify constants if `constants.py` changed
5. Check downstream impact on `digital-twin` for API changes

## Downstream Consumers

This library is consumed by other projects. Breaking changes to public API require:

- Updating all downstream consumers
- Verifying downstream test suites still pass
- Coordinated version bumps if applicable
