# clsfr

Head-to-head benchmark for "System One"-style classification models — lightweight decision
models that answer structured questions (instructions + criteria) on a state:

- **choice** — multi-class routing ("which department should handle this?")
- **noul** — binary yes/no with a probability ("does this text contain a secret?")
- **score** — ordered multi-level rating ("how frustrated is this customer, 0–2?")

Every model answers the same question JSON for the same 8 tasks / 78 cases, defined with gold
labels in [`bench/cases.py`](bench/cases.py).

## Models under test

| Model | Access |
|---|---|
| [Von](https://huggingface.co/wfzyx/von-1.0) | local ModernBERT via [`von-sdk`](https://github.com/wfzyx/von) |
| [GLiNER2](https://huggingface.co/fastino/gliner2-large-v1) | local, adapted to a classification schema |
| Jev (typesafe/jev-1.13) | hosted, via OpenRouter `/api/alpha/decisions` |

## Headline results (8 tasks, 78 cases, Apple MPS)

| Model | micro acc | macro acc | mean latency | cost |
|---|---|---|---|---|
| Jev | **0.974** | **0.972** | ~302 ms | ~$0.000014/call |
| Von 1.0.1 | 0.923 | 0.930 | **~54 ms** | free (local) |
| GLiNER2 | 0.795 | 0.785 | ~93 ms | free (local) |

Full per-task scoreboard, failure examples, and version history:
[`results/benchmark-summary.md`](results/benchmark-summary.md).
Raw per-case records: `results/*.json`.

## Usage

```bash
uv sync

# fetch model weights into models/<org>/<name>
just download wfzyx/von-1.0

# run the suite (backends: von, gliner2, jev — comma-separated)
uv run python -m bench.run --backend von,gliner2 --device mps --out results/run.json
uv run python -m bench.run --backend jev --out results/jev.json
```

Useful flags: `--tasks` (run a subset), `--limit`, `--device` (`mps`/`cpu`/`cuda`),
`--von-path` / `--gliner2-path` (custom weight locations), `--model` (Jev model id).
Jev needs `OPENROUTER_API_KEY` (or `SANDBOX_OPENROUTER_API_KEY`) in the environment.

## Layout

- `bench/cases.py` — the test cases: 8 tasks with gold labels across the three primitives
- `bench/run.py` — harness (CLI, metrics: accuracy, AUC, MAE, latency percentiles)
- `bench/backends/` — one adapter per model
- `results/benchmark-summary.md` — detailed analysis and per-task failure examples
- `results/*.json` — raw benchmark records

## License

[CC0 1.0 Universal](LICENSE) — public domain. The test cases may be reused freely.
