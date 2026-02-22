# Contributing to arqera-math

## Setup

```bash
# Clone and enter the project
cd arqera-math

# Create virtual environment and install
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Development Workflow

### 1. Make your changes

Edit source files in `src/arqera_math/`. Add tests in `tests/`.

### 2. Lint

```bash
ruff check src/
```

### 3. Test

```bash
pytest tests/ -v
```

### 4. Quality gate (both must pass)

```bash
ruff check src/ && pytest tests/ -v
```

### 5. Commit

Use conventional prefixes: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`

Include in AI-assisted commits:
```
Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

## Key Rules

- **Zero external dependencies.** stdlib only.
- **All public API** must be listed in `__all__` in `__init__.py`.
- **Type hints and docstrings** required on all public functions.
- **Return dataclasses**, not raw dicts.

See [CONVENTIONS.md](CONVENTIONS.md) for full engineering standards.
