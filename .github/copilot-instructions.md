# Copilot Instructions — arqera-math

Pure Python 3.11+ math library. **Zero runtime dependencies.**

## Key Rules

- No external packages. stdlib only.
- All public functions go in `__all__` in `__init__.py`.
- Return typed `@dataclass` objects, not raw dicts.
- Type hints and docstrings required on all public functions.
- Constants use bounds validation: `(name, value, min, max, description)`.

## Commands

```bash
# Install
uv pip install -e ".[dev]"

# Lint (must pass before commit)
ruff check src/

# Test (must pass before commit)
pytest tests/ -v

# Quality gate
ruff check src/ && pytest tests/ -v
```

## Style

- Line length: 100
- Ruff rules: E, F, I, W, UP, B, SIM
- Target: Python 3.11+
- Async tests: `asyncio_mode = "strict"`

## Commit Format

Prefixes: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`

Include: `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`
