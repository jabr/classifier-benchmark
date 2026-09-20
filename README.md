# clsfr

Head-to-head benchmark for "System One"-style classification models — lightweight decision
models that answer structured questions (instructions + criteria) on a state:

- **choice** — multi-class routing ("which department should handle this?")
- **noul** — binary yes/no with a probability ("does this text contain a secret?")
- **score** — ordered multi-level rating ("how frustrated is this customer, 0–2?")

Every model answers the same question JSON for the same tasks, defined with gold labels in
[`bench/cases.py`](bench/cases.py). Tasks are grouped into named suites, reported individually
and combined:

- **v1** — the original 8 tasks / 78 cases (unchanged)
- **v2** — 49 tasks / 884 cases: extensions of all 8 v1 tasks (identical question schemas,
  all-new cases across the difficulty spectrum, ids suffixed `_v2`) plus new tasks in adjacent
  domains (expense categorization, on-call routing, churn risk, lead qualification, app-review
  triage) and distant domains (content moderation, code review comments, commit messages,
  cuisine tagging, dietary/vegan and allergen filtering, question deduplication, SQL injection
  review, phishing detection, transaction-fraud rules, ad-policy review, fair-housing
  compliance, travel-policy compliance, PII detection, hazmat shipping, spoiler detection,
  register/formality, newsdesk and article-type tagging, calendar conflicts, document types,
  reading level, insurance-claim priority, symptom and veterinary triage, delivery exceptions,
  city 311 routing, home-service trade routing, contract clause classification, voice-assistant
  intents, grammar checking, meeting action items, gaming reports, warranty claims, weather
  alerts, and return reasons)

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

# run the suite (backends: von, gliner2, laya, jev — comma-separated)
# --suite: v1, v2, comma-separated, or all (default) — per-suite and combined
# scores are reported for every run
uv run python -m bench.run --backend von,gliner2,laya --device mps --out results/run.json
uv run python -m bench.run --backend von --suite v2 --device mps --out results/von-v2.json
uv run python -m bench.run --backend jev --out results/jev.json
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
- `results/benchmark-summary.md` — detailed analysis and per-task failure examples
- `results/*.json` — raw benchmark records (JSON includes `suite_summaries` per suite and
  the combined `summary`)

## License

[CC0 1.0 Universal](LICENSE) — public domain. The test cases may be reused freely.
