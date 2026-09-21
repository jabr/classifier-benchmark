# classifier-benchmark

Head-to-head benchmark for "System One"-style classification models — lightweight decision models that answer structured questions (instructions + criteria) on a state:

- **choice** — multi-class routing ("which department should handle this?")
- **noul** — binary yes/no with a probability ("does this text contain a secret?")
- **score** — ordered multi-level rating ("how frustrated is this customer, 0–2?")

Every model answers the same question JSON for the same tasks. The current headline suite is **v1** — 8 tasks / 78 cases, defined with gold labels in [`cases/v1.toml`](cases/v1.toml). A larger **v2** extension suite is also present in [`cases/v2.toml`](cases/v2.toml) and currently under review; details and progressing results: [`results/v1v2-summary.md`](results/v1v2-summary.md).

Suites are plain TOML data files (schema in [`bench/cases.py`](bench/cases.py)), so harnesses
in languages other than Python can read the test cases directly. Reviewed suites are locked —
`just validate` verifies their content hash against [`cases/hashes.json`](cases/hashes.json);
suites in development stay unlocked until finalized with `just lock <suite>`.

All test cases are synthetic: they were generated and cross-checked by a committee of LLMs (GLM 5.3 Flash, GLM 5.3, Kimi K3, Qwen3.8 2.4T, Qwen3.8 Flash, DeepSeek V4.1 Flash, and MiMo V2.5 Pro), each contributing to task/case definition, expansion, and/or review. Debatable or ambiguous cases were removed before freezing.

Note: these benchmarks are public, and models are free to incorporate the test cases into training data.

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

Full per-task scoreboard, failure examples, and version history: [`results/benchmark-summary.md`](results/benchmark-summary.md). Raw per-case records: `results/*.json`.

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

Useful flags: `--suite` (`v1`/`v2`/comma-separated/`all`, default `all`; core suites only), `--sample` (generated samples from `sources/samples/`: name, comma-separated, or `all`), `--tasks` (run a subset within the selected suites), `--limit`, `--device` (`mps`/`cpu`/`cuda`), `--von-path` / `--gliner2-path` / `--laya-path` (custom weight locations), `--model` (Jev model id). Jev needs `OPENROUTER_API_KEY` (or `SANDBOX_OPENROUTER_API_KEY`) in the environment.

## Layout

- `cases/v1.toml` — the v1 test cases: 8 tasks with gold labels across the three primitives
- `cases/v2.toml` — the v2 suite: extensions of the v1 tasks plus adjacent- and distant-domain tasks (no case overlap with v1)
- `results/benchmark-summary.md` — detailed v1 analysis (all four models) and per-task failure examples
- `results/v1v2-summary.md` — v2 suite composition (in progress) and full-suite results
- `results/*.json` — raw benchmark records (JSON includes `suite_summaries` per suite and the combined `summary`)
- `bench/*` — the Python harness: schema + suite loader and validation, the CLI runner, and model adapter backends
- [`sources/*`](sources/README.md) — external datasets (one real-world, two synthetic from other generators), sampled into bench-format suites with `just gen <source>`; also usable for training-data extraction

## License

[CC0 1.0 Universal](LICENSE) — public domain. The test cases may be reused freely.
