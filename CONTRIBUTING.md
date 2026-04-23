# Contributing

Early-stage project. Issues and PRs welcome, but expect breaking changes until v0.5.

## Dev setup

```bash
git clone https://github.com/<you>/bess-desk.git
cd bess-desk
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Running the hello-world example

```bash
python examples/00_hello_desk.py
```

No API keys needed — uses LLM mock mode.

## Code style

- `ruff check .` — linting
- `ruff format .` — formatting
- `mypy bess_desk` — type checks
- Tests go in `tests/`, named `test_*.py`

## Design principles

Before opening a PR, please read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). The four principles — LLMs advise / code executes, auditable, human-approved, pluggable markets — aren't negotiable.

## Out of scope

PRs that connect to real market execution will not be accepted. This is a research/demo project.
