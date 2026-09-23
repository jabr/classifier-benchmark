# Test cases

| File | Status | Contents |
|---|---|---|
| `v1.toml` | **Frozen** (hash-locked in `hashes.json`) | 8 tasks / 78 cases — the original suite: support triage, email intent, refund policy, urgency, secret detection, frustration, incident severity, review sentiment |
| `v2.toml` | **Locked** (hash-locked in `hashes.json`) | 49 tasks / 866 cases — extensions of every v1 task (same question, all-new cases, ids suffixed `_v2`) plus new adjacent-domain tasks (expense, on-call, churn, leads, app reviews) and distant-domain tasks (moderation, code review, commits, cuisine, diet/allergens, dedup, SQLi, phishing, fraud, ads, fair housing, travel policy, PII, hazmat, spoilers, register, news, calendars, documents, reading level, claims, triage, deliveries, 311, trades, contracts, voice, grammar, action items, gaming, warranties, weather, content types, returns) |

## v1/v2 Provenance

All cases are **synthetic**. They were generated and cross-checked by a committee of LLMs — GLM 5.3 Flash, GLM 5.3, Kimi K3, Qwen3.8 2.4T, Qwen3.8 Flash, DeepSeek V4.1 Flash, and MiMo V2.5 Pro — with two distinct roles:

1. **Generation/expansion.** Models proposed new task domains and case candidates within them. Early iterations favored open-ended expansion: maximize domain spread and case coverage, with only general guidance that states be *realistic* — plausible examples drawn from real operational work (support tickets, code review, expenses, posts) that a classifier could plausibly face in production.
2. **Screening/review.** Different models then reviewed each candidate case, hunting for debatable or ambiguous gold labels. Cases where a careful annotator could reasonably land on two labels — or where the expected answer depended on unstated assumptions — were **removed rather than re-labeled**.

Difficulty was deliberately spread through each task: boundary cases (e.g. day 29 vs day 31 of a 30-day window), keyword decoys (token *management* language that contains no secret), and plain easy items.

## Screening criteria

Every accepted case must satisfy:

- **One defensible gold label.** A careful expert — given the question and the state — would pick the marked answer. If two labels are both defensible, the case is dropped or rewritten, never force-labeled.
- **Realistic states.** Phrased as they would actually arrive: tickets, posts, listings, incident reports, commit messages, menu lines — no meta-descriptions of the scenario.
- **Balanced classes.** Roughly even label distribution, especially on noul tasks (AUC is reported; degenerate positives/negatives make it meaningless).
- **Difficulty has to be earned by the reasoning.** A case is hard because reaching the answer from the state takes real inference — boundary arithmetic, weighing exceptions, decoding a deception, applying the stated criteria to the facts given — not because the wording is vague, the grammar is a gotcha, or the answer was smuggled in from outside the case. Domain knowledge is a normal ingredient of every task here: diet filtering assumes ingredient literacy, triage assumes clinical pattern recognition, code tasks assume programming fluency. Where expected domain mastery ends and smuggled-in trivia begins is a genuinely fuzzy line that already crosses both suites, and we accept that; new cases should lean toward carrying their facts in the state. The bright line we hold to is narrower: a case fails if its answer hinges on what is *impossible to know* — nothing a careful expert could combine from the state and any reasonable domain knowledge reaches the gold label. That is a missing fact, not a test.

## Locking

Every suite is in exactly one of two states:

- **Locked** — final. Recorded scores depend on the content, so the file is not edited; its digest lives in `cases/hashes.json` and `just validate` fails if anything drifts. `v1.toml` and `v2.toml` are locked.
- **Unlocked** — new or in development. Edit freely; no hash entry should exist, and none is created until review concludes.

The transition unlocked → locked is one-way and happens once per suite, when its review is finished: `just lock <suite>`, then commit the updated `hashes.json`. These docs deliberately describe no routine way to change a locked suite; if that ever becomes necessary, it is an exceptional maintainer decision, not a workflow.

Other invariants: task ids must be unique across all suites, and any task declaring `extends = "<task-id>"` must carry a question deep-equal to that task — that is how extension suites (v2's `<id>_v2` tasks, and any future suite) stay directly comparable to what they extend. Both are enforced by the loader/registry. New suites go in their own `cases/<name>.toml`, registered in `bench/suites.py`.
