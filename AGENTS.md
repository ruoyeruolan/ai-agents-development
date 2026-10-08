# Repository Guidelines

## Project Structure & Module Organization

This repository tracks hands-on AI agent study through standalone Python scripts.

- `src/basics/`, `src/demo/apis/`, `src/tool/`, and `src/rag/` contain
  introductory, API, tool-use, and RAG exercises. Use descriptive, lowercase
  package names and underscores between words; add an `__init__.py`.
- `src/config/` holds shared configuration. `src/tool/` contains symbolic
  links to implementations in `src/demo/apis/`; keep their targets valid.
- `src/preprocess/text/` provides pure paragraph, heading, and heading-plus-paragraph
  splitters. RAG scripts read files and pass text and source names to these helpers.
- `src/rag/settings.py` shares prompts and roadmap questions across RAG experiments.
  Model names, output token limits, and API credentials are managed in `src/config/`.
- `src/models/embedding.py` contains the introductory embedding and retrieval demo.
- `plans/ai-agent-development-roadmap.md` defines learning order and deliverables.
  Its HTML companion is maintained separately, without a generator.
- `resources/anthropic-courses/` is the `anthropics/courses` submodule containing
  reference notebooks and assets. Keep personal exercises in `src/`.
- `pyproject.toml` and `uv.lock` manage dependencies; `.python-version` pins 3.13.

## Build, Test, and Development Commands

Run commands from the repository root:

- `uv sync`: install dependencies and the project in editable mode into `.venv`.
- `git submodule update --init --recursive`: fetch course references after cloning.
- `uv run python -m py_compile src/demo/apis/tool_runner_sdk.py`: check syntax
  without executing the script.
- `uv run python src/demo/apis/demo.py`: run an exercise against the configured
  API; this makes a live, potentially billed request.
- `uv run python -m models.embedding`: run as an installed module. Editable
  installation enables cross-package imports without setting `PYTHONPATH`.
- `npx --yes markdownlint-cli2 AGENTS.md plans/ai-agent-development-roadmap.md`:
  check Markdown formatting using the external CLI.

Setuptools discovers packages under `src/`; `uv` installs them automatically.

## Coding Style & Naming Conventions

Use four-space indentation, `snake_case` functions and variables, uppercase
constants, and lowercase snake_case module filenames. Follow nearby synchronous,
procedural examples with explicit tool schemas, type hints, and English teaching
comments. No Python formatter is configured. Preserve the roadmap's unwrapped
paragraphs and file-local `MD013` exemption for adaptive editor wrapping.

## Testing Guidelines

No automated test suite, test framework, or coverage threshold is configured.
Syntax-check changed scripts with `py_compile`; report that this does not validate
runtime behavior. Scripts execute API requests at import time, so avoid importing
them for verification. Pure preprocessing helpers can be checked independently.
Run live checks only when requested. If introducing tests,
use `tests/test_*.py` and document the chosen runner and dependencies.

## Commit & Pull Request Guidelines

Follow the prevalent `type: imperative summary` style, for example
`docs: allow adaptive roadmap wrapping` or `feat: add tool-use exercise`.
Keep commits focused. PRs should explain the learning objective, affected paths,
verification commands and results, and related issues when applicable. Include
screenshots for HTML presentation changes.

## Configuration & Learning Constraints

Scripts load credentials from `~/.secrets` using `python-dotenv`; the repository
`.env` is unused. Preserve matching API endpoints and credentials; never commit
or print secrets. Consult `CLAUDE.md` for detailed conventions. Prefer explanations
and TODO skeletons through Phase 3 unless finished code is requested; introduce
agent frameworks only from Phase 4.
