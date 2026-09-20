# AGENTS.md

Guidance for agents working in this repo.

## What this is

A head-to-head benchmark for "System One"-style decision classifiers — lightweight models that
answer structured questions (instructions + criteria) over a state using three primitives:

- **choice** — multi-class routing ("which department should handle this?")
- **noul** — binary yes/no with a probability ("does this text contain a secret?")
- **score** — ordered multi-level rating (2–10 levels)

Models under test (one adapter each in `bench/backends/`): Von (local ModernBERT via von-sdk),
GLiNER2 and Laya (local), Jev (hosted via OpenRouter's decisions API).

Cases and tasks live in versioned **suites** that are reported separately and combined:
`v1` (8 tasks / 78 cases, original) and `v2` (49 tasks / 869 cases — extensions of every v1
task plus new adjacent- and distant-domain tasks). No overlap between suites.

## Layout

| Path | Contents |
|---|---|
| `bench/cases.py` | **v1 suite — frozen, do not modify** (recorded scores depend on it) |
| `bench/cases_v2.py` | v2 suite; extension tasks reuse v1 question objects with `_v2` ids |
| `bench/suites.py` | suite registry, id resolution, plan building |
| `bench/run.py` | harness/CLI; per-suite and combined metrics (acc, AUC, MAE, latency) |
| `bench/backends/` | model adapters behind `create_backend(name, **kwargs)` |
| `results/` | raw run records + `benchmark-summary.md` (analysis) — only add/extend when asked |
| `models/<org>/<name>` | local weights, fetched via `just download <org>/<name>` |

Question schemas come from `von.types` (`Choice`, `Noul`, `Score`); `Case`/`Task` dataclasses
live in `bench/cases.py`. A task's question JSON is fully defined by its `Question` object —
identical questions across v1/v2 are enforced by importing the v1 builder's question.

## Running benchmarks

**Never run `bench.run`, and never download model weights, unless the user explicitly asks.**
Runs take real time, Jev costs money via OpenRouter, and the user decides when numbers are
generated.

When asked, the commands are:

```bash
uv sync
uv run python -m bench.run --backend von --device mps --suite all --out results/run.json
uv run python -m bench.run --backend jev --out results/jev.json   # needs OPENROUTER_API_KEY
```

- `--suite`: `v1`, `v2`, comma-separated, or `all` (default). `--tasks` filters within the
  selected suites. `--limit` truncates cases per task (smoke tests).
- Jev auth: `OPENROUTER_API_KEY` or `SANDBOX_OPENROUTER_API_KEY`.
- In sandboxed sessions `--device mps` can fail (torch can't query `sw_vers`); CPU produces
  identical accuracy, only latency differs. Use `mps` on the real machine.

## Adding or changing cases

- All case edits go in `bench/cases_v2.py`; register new task functions in the right bucket
  (`EXTENSION_TASK_FUNCTIONS`, `NEW_SIMILAR_TASK_FUNCTIONS`, `NEW_DISTANT_TASK_FUNCTIONS`).
- Task ids must be unique across both suites (checked at import in `bench/suites.py`).
- Gold labels must be defensible — a careful majority of annotators should agree — and classes
  should be roughly balanced, especially for noul tasks (AUC is reported).
- Mix difficulties deliberately: boundary cases, keyword decoys, and plain easy items.
- Keep states realistic (support tickets, review comments, code, expenses, posts).
- Safe validation without any model: `uv run python -c "import bench.suites"` plus a quick
  check that expected labels match each task's type (bool for noul, valid option key for
  choice, in-range int for score).

## Style

- Python 3.14, `uv` for env/running. 2-space indentation, single blank lines between functions.
- No comments unless they explain *why*; always preserve existing comments.
- No linter or test suite is configured; `uv run python -m py_compile <files>` is the quick
  sanity check. Use `jq` for JSON.
