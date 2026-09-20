# classifier-benchmark

Head-to-head benchmark for "System One"-style classification models — lightweight decision
models that answer structured questions (instructions + criteria) on a state:

- **choice** — multi-class routing ("which department should handle this?")
- **noul** — binary yes/no with a probability ("does this text contain a secret?")
- **score** — ordered multi-level rating ("how frustrated is this customer, 0–2?")

Every model answers the same question JSON for the same tasks. The current headline suite is
**v1** — 8 tasks / 78 cases, defined with gold labels in [`bench/cases.py`](bench/cases.py).
A larger **v2** extension suite is also present in `bench/cases_v2.py` and currently under
review; details and progressing results: [`results/v1v2-summary.md`](results/v1v2-summary.md).

All test cases are synthetic: they were generated and cross-checked by a committee of LLMs
(GLM 5.3 Flash, GLM 5.3, Kimi K3, Qwen3.8 2.4T, Qwen3.8 Flash, DeepSeek V4.1 Flash, and
MiMo V2.5 Pro), each contributing to task/case definition, expansion, and/or review.
Debatable or ambiguous cases were removed before freezing.

## Models under test

| Model | Access |
|---|---|
| [Von](https://huggingface.co/wfzyx/von-1.0) | local ModernBERT via [`von-sdk`](https://github.com/wfzyx/von) |
| [GLiNER2](https://huggingface.co/fastino/gliner2-large-v1) | local, adapted to a classification schema |
| [Laya](https://huggingface.co/convaiinnovations/laya) | local, native System One schema via the `laya` package |
| Jev (typesafe/jev-1.13) | hosted, via OpenRouter `/api/alpha/decisions` |

## Headline results (v1: 8 tasks, 78 cases, Apple MPS)

| Model | micro acc | macro acc | mean latency | cost |
|---|---|---|---|---|
| Jev | **0.974** | **0.972** | ~302 ms | ~$0.000014/call |
| Von 1.0.1 | 0.923 | 0.930 | ~54 ms | free (local) |
| GLiNER2 | 0.795 | 0.785 | ~93 ms | free (local) |
| Laya | 0.615 | 0.619 | **~48 ms** | free (local) |

Full per-task scoreboard, failure examples, and version history:
[`results/benchmark-summary.md`](results/benchmark-summary.md).
Raw per-case records: `results/*.json`.

## Usage

```bash
uv sync

# fetch model weights into models/<org>/<name>
just download wfzyx/von-1.0
just download fastino/gliner2-large-v1
just download convaiinnovations/laya

# run the v1 suite (backends: von, gliner2, laya, jev — comma-separated)
uv run python -m bench.run --backend von,gliner2,laya --suite v1 --device mps --out results/run.json
uv run python -m bench.run --backend jev --suite v1 --out results/jev.json
```

Useful flags: `--suite` (`v1`/`v2`/comma-separated/`all`, default `all`), `--tasks` (run a
subset within the selected suites), `--limit`, `--device` (`mps`/`cpu`/`cuda`),
`--von-path` / `--gliner2-path` / `--laya-path` (custom weight locations), `--model` (Jev model id).
Jev needs `OPENROUTER_API_KEY` (or `SANDBOX_OPENROUTER_API_KEY`) in the environment.

## Layout

- `bench/cases.py` — the v1 suite: 8 tasks with gold labels across the three primitives
- `bench/cases_v2.py` — the v2 suite: extensions of the v1 tasks plus adjacent- and
  distant-domain tasks (no case overlap with v1)
- `bench/suites.py` — suite registry (v1/v2) and task lookup
- `bench/run.py` — harness (CLI, suite/combined metrics, accuracy, AUC, MAE, latency percentiles)
- `bench/backends/` — one adapter per model
- `results/benchmark-summary.md` — detailed v1 analysis (all four models) and per-task failure examples
- `results/v1v2-summary.md` — v2 suite composition (in progress) and full-suite results
- `results/*.json` — raw benchmark records (JSON includes `suite_summaries` per suite and
  the combined `summary`)

## License

[CC0 1.0 Universal](LICENSE) — public domain. The test cases may be reused freely.
