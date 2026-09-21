# Real-data sources

External, real-world datasets for the benchmark, plus generators that sample them into bench-format suite files. The same loaders give you raw rows, so they double as starting points for training-data extraction.

## Sources

| Source | Dataset | Data | Labels |
|---|---|---|---|
| `cfpb` | [sovai/cfpb_complaints](https://huggingface.co/datasets/sovai/cfpb_complaints) | real CFPB complaint narratives (live mirror) | consumer's self-selected `issue` at filing — CFPB scrubs PII but never verifies or corrects categories, and the issue menu cannot represent everything consumers complain about; screen every case against its narrative before use |
| `support_tickets` | [cngchis/Support-Ticket-Router-12K-Cleaned](https://huggingface.co/datasets/cngchis/Support-Ticket-Router-12K-Cleaned) | synthetic support tickets (GPT-4-class generated, filtered/cleaned) | intent assigned at generation |
| `triageiq` | [coldstart88/triageiq-dataset](https://huggingface.co/datasets/coldstart88/triageiq-dataset) | synthetic support tickets | generation-assigned, three questions extractable: `triageiq` (5-way category, choice), `triageiq_negative` (negative sentiment, noul), `triageiq_urgency` (3-level urgency, score) |

Samples come from the eval-relevant splits (and for cfpb, the filed-issue→category mapping) so a task poses the problem a practitioner would pose on that data.

## Generating samples

```bash
just gen cfpb --seed 48110          # or another source, any 16-bit seed
```

That draws a balanced sample (`--n`, default 40 cases, equal per class; inputs capped at `--max-words`, default 120; emails/phones redacted) deterministically from the seed, and writes an unlocked suite TOML to `sources/samples/` with a provenance header (source, seed, filters, date). Skip `--seed` and one is generated for you. `sources/samples/` is a scratch working directory (git-ignored) — bench auto-discovers whatever is in it: run generated samples with `--sample <name>` (e.g. `--sample cfpb-bbee`) or `--sample all`; `--suite` keeps meaning the core suites only.

Kinds of use: run a sample as-is for an OOD check (`--sample all`), or generate several seeds of a source over time (`cfpb-…`, `cfpb-…`) as an accumulative moving target — a model cannot have tuned on a sample that didn't exist when it was built.

## Making suites from samples

When a sample proves its worth — defensible golds under the screening rules in `cases/README.md`, interesting miss patterns — promote it: copy the cases into a new task in a future suite under `cases/` with its own task id, and review it like any other task. The sample file stays behind as provenance. Once a sample has been promoted, don't run both in the same benchmark session: the shared states would be counted twice in combined metrics.

## Extraction

The loaders in `sources/common.py` (`ds_server_rows`, `hf_rows`) are generic: point them at any Hub dataset for row access, whether to generate benchmark samples or to pull training data (samples or whole datasets). What downstream consumers do with the data is up to them.
