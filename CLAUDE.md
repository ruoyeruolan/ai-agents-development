# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal study repo for learning AI agent development. There is no application, no package to
build, and no tests. The deliverable is **practice scripts written by hand while working through a
roadmap**.

`plans/ai-agent-development-roadmap.md` is the source of truth for what gets built next. Phases 0–6,
each of Phases 0–5 with a **Ship** deliverable and a **Checkpoint** (Phase 6 is capstone + career
packaging instead). Read it before proposing work — it sets the ordering, the tech choices, and the
two hard constraints below.

**Pedagogy constraint (roadmap L254): the user types the code themselves through at least Phase 3.**
Default to a skeleton with TODOs, a review of code they wrote, or a checkpoint quiz. Write a finished
implementation only when explicitly asked.

**No frameworks before Phase 4.** Phases 0–3 are raw SDK calls and hand-rolled loops on purpose;
LangGraph and MCP enter at Phase 4. Do not introduce LangChain/LangGraph/CrewAI into `phase01`-era code.

## Commands

```bash
# syntax-check an edit — the ONLY free verification that exists here
uv run python -m py_compile practice/phase01/<script>.py

# run a script (from repo root) — MAKES A LIVE, BILLED API CALL
uv run python practice/phase01/demo.py

# submodule, needed only on a fresh clone
git submodule update --init --recursive
```

**There is no test, lint, format, or type-check command.** `pyproject.toml` declares a
`[tool.pyright]` block, but pyright is installed neither in `.venv` nor globally; neither are pytest,
ruff, black, or mypy. Do not invent a `pytest`/`ruff`/`make` invocation.

Every script fires its API call at import time — no `__main__` guard, no argparse, prompts hardcoded.
So never run one to "verify" an edit; `py_compile` it instead.

## Credentials

Secrets load from **`~/.secrets`** — `load_dotenv(Path.home() / ".secrets")` in every script — **not**
the repo `.env`. The repo `.env` is a stale leftover (`DEEPSEEK_API_KEY`, lowercase `base_url`) that
no script reads.

`~/.secrets` defines `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`,
`DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`.

**Everything routes through a proxy gateway, including `demo.py`.** The five `phase01` tool scripts
build `anthropic.Anthropic(auth_token=..., base_url=...)` explicitly. `demo.py` passes only
`api_key=` — but the SDK falls back to `ANTHROPIC_BASE_URL` from the environment
(`anthropic/_client.py:225`), so it reaches the same gateway. Models are `"deepseek-v4-pro[1m]"`
(`calender.py`, `agentic-loop.py`, `multi-tools-parallel-calls.py`, `parallel-too-call-weather.py`),
plain `"deepseek-v4-pro"` (`tool-runner-sdk.py`, `Phase0/hello-agent.py`), and `"claude-sonnet-4-6"`
(`demo.py`). Anthropic-SDK code against DeepSeek models is deliberate — the roadmap says develop on
the cheapest tier.

`Phase0/hello-agent.py` is the one OpenAI-SDK script. It passes `reasoning_effort="high"` and
`extra_body={"thinking": {"type": "enabled"}}` — DeepSeek-gateway extensions, not portable OpenAI
kwargs. Keep them when editing it.

## Layout

- `plans/` — the roadmap. The `.md` is live. The `.html` is a **hand-authored, stale** rendering
  (bespoke CSS, no generator) frozen at commit `1cab741`, 5 later commits behind the `.md`.
- `practice/<phase>/` — the scripts. **Naming is inconsistent: `Phase0/` vs `phase01/`.** Use the
  newer lowercase zero-padded form for new dirs; don't silently rename the old one.
- `resources/courses/` — submodule of `anthropics/courses` (reference notebooks; their deps are not
  in this lockfile).
- `README.md` is empty (0 bytes) — an open Phase 0 item.

## What each phase01 script teaches

| Script | Concept |
|---|---|
| `demo.py` | bare `messages.create` smoke test, no tools (16 lines) |
| `calender.py` | **Ring 1** — one tool, one turn: single `tool_use`, one manual `tool_result` follow-up, no loop |
| `agentic-loop.py` | hand-rolled `while` loop over one tool + strict post-loop `stop_reason` validation (incl. an explicit `max_tokens` check) |
| `multi-tools-parallel-calls.py` | **Ring 3** — several tools, all `tool_use` blocks per turn, per-tool `is_error` results, turn logging |
| `parallel-too-call-weather.py` | observing parallel tool calls with two toy tools, one round-trip |
| `tool-runner-sdk.py` | the Ring 3 scenario via `@beta_tool` + `client.beta.messages.tool_runner(...).until_done()` — an A/B against the manual loop (66 lines vs 172) |

Only `calender.py` and `multi-tools-parallel-calls.py` actually carry a `# Ring N:` header — there is
no Ring 2 anywhere, and "Ring" never appears in the roadmap. Worth continuing on new tool-use
scripts, and backfilling the gaps is in scope.

**`tool_choice` is the axis these exercises turn on.** Single-tool scripts pass
`tool_choice={"type": "auto", "disable_parallel_tool_use": True}` on *every* `messages.create`, which
is what makes `next(...)` safe for grabbing one block. Parallel scripts omit `tool_choice` entirely
and must iterate all `tool_use` blocks. Choose deliberately; copying the wrong half silently breaks
the lesson.

## House style for a new practice script

The pattern is `calender.py`, `agentic-loop.py`, and `multi-tools-parallel-calls.py`. The other three
are deliberate outliers — `demo.py` (no-tool smoke test), `parallel-too-call-weather.py` (pasted
tutorial code: untyped `tools`, `✓`/`✗` markers), `tool-runner-sdk.py` (the SDK counter-example).

- Flat top-level procedural script. No `if __name__ == "__main__":`, no `main()`, no argparse. Sync
  only, no `async`. Lowercase kebab-case filenames.
- `load_dotenv(Path.home() / ".secrets")` right after imports, then `os.environ.get(...)`.
- Tools inline as `tools: List[ToolParam] = [...]` with hand-written JSON Schema — not Pydantic, not
  helpers. Dispatch through one `run_tool(name, tool_input)` with a flat `if name == ...` chain
  returning simulated results.
- Loop: first request *before* the loop, then `while response.stop_reason == "tool_use":`. Append
  `{"role": "assistant", "content": response.content}`, then `{"role": "user", "content": tool_results}`.
  Serialize results with `json.dumps(result)`.
- After the loop, `raise RuntimeError` on any `stop_reason` but `end_turn`. Return tool failures to
  the model as `{"type": "tool_result", ..., "is_error": True}` rather than crashing.
- Hoist the token cap: `MAX_OUTPUT_TOKENS = 10240` for new loops (`multi-tools-parallel-calls.py`
  spells it `MAX_TOKEN`; the single-turn scripts just pass `max_tokens=1024` inline).
- Heavy `#` comments explaining each block — this is teaching code, comments always in English.
  Docstrings only where load-bearing (`@beta_tool`, where the SDK parses them into the schema).
- `print(..., flush=True)` when writing a step trace (only `multi-tools-parallel-calls.py` does this
  today, and it is the model to copy) — never `logging`.
- **`agentic-loop.py` raises its `RuntimeError` messages in Chinese; `multi-tools-parallel-calls.py`
  raises the same conditions in English. That is not an encoding bug — leave it.** Use English in new code.

If asked to write a new loop: the roadmap mandates a **max-iteration guard and a printed trace**
(L89, L98). Neither existing loop has an iteration cap, only a `stop_reason` check. Adding one is in scope.

## Gotchas

- Two tracked *filenames* carry typos and are the real paths: `calender.py` (calendar) and
  `parallel-too-call-weather.py` (tool). Don't rename them incidentally.
- Two genuine bugs, worth flagging rather than copying: `calender.py` re-sends the first user turn to
  the follow-up call with the address mistyped `@gmial.com` (the original used `@gmail.com`), so the
  replayed history diverges; and `multi-tools-parallel-calls.py`'s `run_tool` unknown-tool branch says
  `return ValueError(...)` where it means `raise` — it only appears to work because `json.dumps` then
  throws into the enclosing `except`.
- `.python-version` pins `3.13` while `pyproject.toml` says `requires-python = ">=3.12.4"`. The venv
  is uv-managed CPython 3.13.15; system `python3` is 3.14.4. Always go through `uv run`.
- `.gitignore` has **no trailing newline** — appending a rule without adding one first corrupts the
  last entry into `.rememberNEWRULE`. It also contains the unanchored glob `*db`, which hides any
  path component ending in `db`, not just `.db` files; today that is the only thing concealing the
  1.5 MB `ruvector.db` at the repo root.
- `.claude-flow/`, `.omc/`, `.remember/`, `.swarm/` and `ruvector.db` belong to unrelated agent
  tooling, not this project. Don't read them for context or tidy them up.
- `.DS_Store` and `plans/.DS_Store` are tracked, with no ignore rule.
- `async>=0.6.2` in `pyproject.toml` is the ancient unrelated PyPI package, imported by nothing —
  almost certainly a stray `uv add`. Pydantic is not declared but resolves today only transitively via
  `anthropic`/`openai`; declare it explicitly before Phase 1's structured-output work.
- Commit style is mixed. Most use `type: imperative lowercase summary` (`feat:`, `docs:`, `chore:`,
  `fix:`); four of eleven have no prefix. Match the prefixed form.

## Open roadmap items

Nothing in the progress tracker (L258–265) is ticked. The code on disk has already reached Phase 2
material (agent loop, multi-tool, error handling) while still living in `phase01/`. Unshipped: Phase
1's **CLI chat assistant** (multi-turn memory, streaming, personas, `/save`, token/cost meter), Phase
2's **research agent** (web search + calculator + file I/O, max-iteration guard, readable trace), and
Phase 0's streaming + cost print in `hello-agent.py` plus a non-empty root README.
