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
| `cases/v1.toml` | **v1 suite data — frozen, do not modify** (recorded scores depend on it); hash-locked in `cases/hashes.json` |
| `cases/v2.toml` | v2 suite data (49 tasks / 869 cases, currently under review); extension tasks duplicate their v1 question with `_v2` ids |
| `cases/hashes.json` | content hash per locked suite |
| `bench/cases.py` | bench-owned schema: `Task`/`Case` dataclasses, question types (`Choice`/`Noul`/`Score` in the System One wire shape), TOML loader/validation |
| `bench/suites.py` | suite registry, id resolution, plan building; enforces unique ids and v1↔v2 question equality |
| `bench/validate.py` | suite structure + hash validation; `just validate` to run, `just relock <suite>` to re-hash after deliberate edits |
| `bench/run.py` | harness/CLI; per-suite and combined metrics (acc, AUC, MAE, latency) |
| `bench/backends/` | model adapters behind `create_backend(name, **kwargs)` |
| `results/` | raw run records + `benchmark-summary.md` (analysis) — only add/extend when asked |
| `models/<org>/<name>` | local weights, fetched via `just download <org>/<name>` |

The question schema is bench-owned (`bench/cases.py`), defined as the System One wire shape
(`type`/`instructions`/`criteria`) that the typesafe/jev API also speaks; backends convert to
their model's native format. `von.types` is only used inside `bench/backends/von.py` when
talking to the von-sdk itself. Test cases live in TOML data files, so harnesses in other
languages can read them directly.

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

- All case edits go in `cases/v2.toml`; extension tasks (`*_v2` ids) must keep their
  question deep-equal to their v1 original (checked in `bench/suites.py`).
- Task ids must be unique across both suites (checked at import in `bench/suites.py`).
- v1 is hash-locked: `just validate` fails if it changed. Breaking the freeze deliberately
  means `just relock v1` (and a commit message that says why). Same for v2 once edits are
  intentional: edit, then `just relock v2` and commit the new hash.
- Gold labels must be defensible — a careful majority of annotators should agree — and classes
  should be roughly balanced, especially for noul tasks (AUC is reported).
- Mix difficulties deliberately: boundary cases, keyword decoys, and plain easy items.
- Keep states realistic (support tickets, review comments, code, expenses, posts).
- Safe validation without any model: `uv run python -m bench.validate` (parses both TOML
  suites, checks the invariants, verifies locked hashes).

## Style

- Python 3.14, `uv` for env/running. 2-space indentation, single blank lines between functions.
- No comments unless they explain *why*; always preserve existing comments.
- No linter or test suite is configured; `uv run python -m py_compile <files>` is the quick
  sanity check. Use `jq` for JSON.
