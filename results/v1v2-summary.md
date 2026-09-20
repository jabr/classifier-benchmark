# Full suite results (v1 + v2): 947 cases across four System One models

Head-to-head across both test suites: **v1** (8 tasks / 78 cases, `bench/cases.py`) and **v2**
(49 tasks / 869 cases, `bench/cases_v2.py`). No case overlap between suites.

**Status:** v2 results are preliminary — shared with the Von project for review before being promoted
to the headline comparison in the README.

Participants:

- **Von 1.0.1** (`wfzyx/von-1.0`), local ModernBERT on Apple MPS, fp16, calibrated T=1.1692
- **Jev** (`typesafe/jev-1.13`), hosted via OpenRouter `/api/alpha/decisions`, one request per case
  (~$0.013 total for 947 requests at ~$0.000014/call)
- **GLiNER2** (`fastino/gliner2-large-v1`), local; questions with parentheses are paraphrased for its
  schema compiler (adapter-level)
- **Laya** (`convaiinnovations/laya`), local, native System One schema

The v1 block reproduces the earlier recorded runs exactly for every model
(Von 0.923, Jev 0.974, GLiNER2 0.795, Laya 0.615 micro — see `benchmark-summary.md` for the v1-only
version history and failure archive).

v2 suite composition:

- **Extensions of all 8 v1 tasks** — identical question schemas reused under `_v2` ids, all-new
  cases across the difficulty spectrum
- **New tasks in adjacent domains** — expense categorization, on-call routing, churn risk, lead
  qualification, app-review triage
- **New tasks in distant domains** — content moderation, code review comments, commit messages,
  cuisine tagging, dietary/vegan and allergen filtering, question deduplication, SQL injection
  review, phishing detection, transaction-fraud rules, ad-policy review, fair-housing
  compliance, travel-policy compliance, PII detection, hazmat shipping, spoiler detection,
  register/formality, newsdesk and article-type tagging, calendar conflicts, document types,
  reading level, insurance-claim priority, symptom and veterinary triage, delivery exceptions,
  city 311 routing, home-service trade routing, contract clause classification, voice-assistant
  intents, grammar checking, meeting action items, gaming reports, warranty claims, weather
  alerts, and return reasons

## Headline

| Suite | n | Von micro | Von macro | Jev micro | Jev macro | GLiNER2 micro | GLiNER2 macro | Laya micro | Laya macro |
|---|---|---|---|---|---|---|---|---|---|
| v1 | 78 | 0.923 | 0.930 | **0.974** | **0.972** | 0.795 | 0.785 | 0.615 | 0.619 |
| v2 | 869 | 0.666 | 0.667 | **0.964** | **0.966** | 0.688 | 0.684 | 0.585 | 0.583 |
| **combined** | 947 | 0.687 | **0.704** | **0.965** | **0.967** | **0.697** | 0.698 | 0.587 | 0.588 |

| | mean latency / case | wall time (947 cases) |
|---|---|---|
| Laya (MPS) | **46 ms** | **76 s** |
| Von (MPS) | 55 ms | 57 s |
| GLiNER2 (MPS) | 73 ms | 80 s |
| Jev | ~330 ms | ~5.2 min |

Robustness to the v2 shift (micro, v1 → v2): Jev −1.0 pt (0.974 → 0.964), Laya −3.1 (0.615 → 0.585),
GLiNER2 −10.7 (0.795 → 0.688), Von −25.7 (0.923 → 0.666). Because their slopes differ, combined micro
ranks GLiNER2 (0.697) narrowly over Von (0.687), while macro keeps Von ahead (0.704 vs 0.698) — Von
piles up near-perfect extension tasks and collapses on a few, GLiNER2 scatters more uniformly.

## v1 (8 tasks / 78 cases)

| Task (type) | n | Von | Jev | GLiNER2 | Laya |
|---|---|---|---|---|---|
| support_department (choice) | 15 | 0.867 | **1.000** | 0.933 | 0.533 |
| email_intent (choice) | 10 | **1.000** | **1.000** | 0.900 | 0.900 |
| refund_eligible (noul) | 10 | 0.700 | **1.000** | 0.500 | 0.700 |
| urgency (noul) | 8 | **1.000** | **1.000** | **1.000** | 0.875 |
| secret_leak (noul) | 8 | 0.875 | **1.000** | 0.500 | 0.500 |
| frustration_level (score) | 9 | **1.000** | **1.000** | **1.000** | 0.667 |
| incident_severity (score) | 9 | **1.000** | 0.778 | 0.556 | 0.444 |
| review_sentiment (score) | 9 | **1.000** | **1.000** | 0.889 | 0.333 |

## v2 (49 tasks / 869 cases)

First the eight extensions of v1 questions, then the new tasks in authoring order.

| Task (type) | n | Von | Jev | GLiNER2 | Laya |
|---|---|---|---|---|---|
| support_department_v2 (choice) | 17 | 0.765 | **1.000** | 0.882 | 0.588 |
| email_intent_v2 (choice) | 15 | 0.800 | **1.000** | 0.800 | 0.733 |
| refund_eligible_v2 (noul) | 17 | 0.647 | **1.000** | 0.529 | 0.412 |
| urgency_v2 (noul) | 18 | 0.889 | **1.000** | **1.000** | 0.722 |
| secret_leak_v2 (noul) | 16 | 0.688 | **0.875** | 0.438 | 0.562 |
| frustration_level_v2 (score) | 18 | 0.556 | **0.944** | 0.667 | 0.500 |
| incident_severity_v2 (score) | 14 | 0.786 | **1.000** | 0.357 | 0.214 |
| review_sentiment_v2 (score) | 18 | 0.611 | **0.944** | 0.500 | 0.278 |
| expense_category (choice) | 18 | 0.833 | **1.000** | 0.778 | 0.778 |
| oncall_route (choice) | 17 | **1.000** | **1.000** | 0.882 | 0.824 |
| churn_risk (score) | 18 | 0.778 | **1.000** | 0.833 | 0.389 |
| lead_qualification (score) | 16 | 0.625 | **0.938** | 0.562 | 0.438 |
| app_review_intent (choice) | 16 | 0.875 | **1.000** | 0.938 | 0.938 |
| content_moderation (choice) | 18 | 0.722 | **1.000** | 0.611 | 0.722 |
| code_review_intent (choice) | 17 | 0.706 | **0.941** | 0.412 | 0.412 |
| commit_intent (choice) | 16 | 0.375 | **0.938** | 0.500 | 0.812 |
| recipe_cuisine (choice) | 18 | 0.833 | **1.000** | 0.889 | 0.556 |
| question_duplicate (noul) | 16 | 0.750 | **1.000** | 0.500 | 0.688 |
| sql_injection_risk (noul) | 15 | 0.533 | **1.000** | 0.467 | 0.333 |
| travel_policy_violation (noul) | 17 | 0.647 | **1.000** | 0.647 | 0.588 |
| contains_pii (noul) | 17 | 0.706 | **0.941** | 0.765 | 0.765 |
| contains_spoiler (noul) | 16 | 0.562 | **0.938** | 0.562 | 0.500 |
| formality_level (score) | 16 | 0.438 | **0.938** | 0.562 | 0.188 |
| phishing_email (noul) | 17 | 0.471 | **1.000** | 0.882 | 0.647 |
| meeting_conflict (noul) | 17 | 0.529 | **1.000** | 0.529 | 0.471 |
| hazmat_shipping (noul) | 16 | 0.438 | **1.000** | 0.562 | 0.562 |
| dietary_vegan (noul) | 17 | 0.471 | **1.000** | 0.529 | 0.588 |
| news_topic (choice) | 17 | 0.941 | **1.000** | 0.941 | 0.765 |
| document_type (choice) | 15 | 0.800 | **1.000** | 0.800 | 0.733 |
| reading_level (score) | 16 | 0.375 | **1.000** | 0.500 | 0.375 |
| insurance_claim_priority (score) | 16 | 0.625 | **0.875** | 0.812 | 0.375 |
| symptom_triage (score) | 19 | 0.421 | **0.895** | 0.368 | 0.421 |
| delivery_exception (choice) | 19 | 0.895 | **1.000** | 0.947 | **1.000** |
| city_service_request (choice) | 19 | 0.947 | **1.000** | 0.895 | 0.737 |
| ad_policy_violation (noul) | 16 | 0.562 | **1.000** | 0.625 | 0.750 |
| fair_housing_violation (noul) | 19 | 0.684 | **0.947** | 0.526 | 0.474 |
| contract_clause_type (choice) | 17 | 0.941 | **1.000** | 0.941 | 0.882 |
| voice_assistant_intent (choice) | 20 | 0.900 | **1.000** | 0.950 | 0.750 |
| grammar_issue (choice) | 22 | 0.182 | **0.864** | 0.227 | 0.227 |
| action_item_assignment (noul) | 19 | 0.842 | **0.947** | 0.632 | 0.579 |
| suspicious_transaction (noul) | 17 | 0.529 | **1.000** | 0.529 | 0.588 |
| return_reason (choice) | 18 | 0.611 | **1.000** | 0.944 | 0.500 |
| allergen_present (noul) | 22 | 0.591 | **0.909** | 0.545 | 0.500 |
| home_service_routing (choice) | 23 | 0.913 | **1.000** | 0.957 | 0.826 |
| gaming_report_type (choice) | 20 | 0.800 | **0.900** | 0.750 | 0.750 |
| warranty_claim_eligible (noul) | 20 | 0.450 | **0.850** | 0.500 | 0.500 |
| weather_alert_severity (score) | 22 | 0.545 | 0.864 | **0.909** | 0.545 |
| content_type (choice) | 22 | 0.636 | **0.955** | 0.909 | 0.636 |
| veterinary_triage (score) | 20 | 0.450 | **0.950** | 0.700 | 0.450 |

## Analysis

### Von — mode collapse and trigger drift off its training distribution

The 1.0.1 gains hold only where states look like its training data:

- `grammar_issue` is the worst cell in the whole benchmark (0.182): 20 of 22 answers are
  `subject_verb_agreement` regardless of whether the sentence has a spelling error, a punctuation
  problem, or nothing wrong at all.
- `commit_intent` (0.375): every `refactor` drifts to `fix`/`test`, `docs` to `test`, `chore` to `fix` —
  everything lands on "safe maintenance commit".
- Rating scales compress downward off-domain: `reading_level` 0.375 (level 2→0 four times, 1→0 four
  times), `formality_level` 0.438 (3→2 five times), `symptom_triage` 0.421, `veterinary_triage` 0.450.
- Binary `noul` with unfamiliar criteria over-triggers or noise-triggers: hazmat 0.438, dietary_vegan
  0.471, phishing 0.471, warranty 0.450, suspicious_transaction 0.529, ad_policy 0.562.
- What survives: crisp taxonomy routing — `oncall_route` 1.000, `city_service_request` 0.947,
  `news_topic` 0.941, `contract_clause_type` 0.941, `home_service_routing` 0.913 — i.e. short states,
  flat label sets, single obvious category. AUC details per noul task are in `v1v2-von.json`.

### Jev — 31 errors in 869 cases, all small and near-boundary

- Over-flags on two binary tasks with borderline "no" cases: `secret_leak_v2` and `contains_pii`
  (also `action_item_assignment`, `allergen_present` ×2) — `yes` on states that discuss tokens,
  identifiers, or assignments without containing one.
- Adjacent-level severity/rating misses: `weather_alert_severity` (0→1, 1→3 twice), `insurance_claim_priority`
  (1→2, 1→0), `symptom_triage` (3→2, 0→1), `formality_level` 3→2, `veterinary_triage` 1→0.
- Near-synonym category confusions in choice: `gaming_report_type` smurfing→cheating, boosting→other;
  `code_review_intent` nit→refactor; `commit_intent` refactor→chore; `content_type` feature→news_report.
- `warranty_claim_eligible` is its weakest task (0.850, three yes→no).
- The one v1 cell it loses was `incident_severity` (0.778 vs Von's 1.000; the same two adjacent-level
  boundary cases); those disappear on the small `incident_severity_v2` extension (Jev 1.000), so it is
  not a systematic Von advantage.

### GLiNER2 — the gentlest non-Jev slope, still keyword-driven

- Transfers better than Von to new domains (v2 micro 0.688 vs 0.666) and owns several social-language
  cells outright: `urgency_v2` 1.000, `weather_alert_severity` 0.909 (nobody else above 0.6),
  `insurance_claim_priority` 0.812, `phishing_email` 0.882, `return_reason` 0.944, `voice_assistant_intent`
  0.950, `home_service_routing` 0.957.
- The keyword-flood failure mode persists on new material: `secret_leak_v2` 0.438 (over-flags discussion
  of tokens), `sql_injection_risk` 0.467, `incident_severity_v2` 0.357 and `symptom_triage` 0.368
  (worse than Von there), and `grammar_issue` 0.227.
- Extension tasks that are easy for Von get *harder* for it (`frustration_level_v2` 0.667 vs 1.000 on
  v1; `review_sentiment_v2` 0.500 vs 0.889) while Von's weak cells stay weak — hence flatter, lower
  macro on v2 than its micro suggests.

### Laya — smallest v1→v2 drop, from the lowest base

- Nearly flat in absolute terms (0.615 → 0.585), but starting from last place; combined 0.587/0.588.
- The cool-grading attractor dominates every new rating task: `formality_level` 0.188 (worst cell of
  the four models), `incident_severity_v2` 0.214, `review_sentiment_v2` 0.278 — while most misses stay
  within one level (`within_1` 0.88 / 0.93 / 0.67 on those three; details in `v1v2-laya.json`).
- Genuine highlights: `delivery_exception` 1.000 (ties Jev, beats both other locals), `commit_intent`
  0.812 (second only to Jev — it reads commit messages better than Von does), `question_duplicate`
  0.688 (best of the locals), and a respectable `content_moderation` 0.722 / `ad_policy_violation` 0.750.
- Fastest per-case clock (46 ms mean on MPS) and the best noul *ordering* of the locals on
  `hazmat_shipping` (AUC 0.92 vs GLiNER2 0.68 and Von 0.61, against 0.56 accuracy — ranking is real,
  the 0.5 threshold just doesn't know it).

## Takeaway

Jev generalizes to suitably out-of-domain tasks essentially unchanged (−1 point micro across 869 new
cases); the three local models pay for the shift in very different currencies — Von with concentrated
mode-collapses (grammar/commit/ratings), GLiNER2 with keyword-driven over-triggering, Laya with a
compressed rating scale that reads cool on everything. At ~6× the latency and a fraction of a cent per
1k calls, Jev remains the accuracy candidate; the locals remain fast free baselines whose failure
signatures are easy to detect in production (low-entropy wrong answers, saturated confidence on
trigger words, mid-scale mass).

## Reproduce

```
uv run python -m bench.run --backend von --suite all --device mps --out results/v1v2-von.json
uv run python -m bench.run --backend jev --suite all --out results/v1v2-jev.json
uv run python -m bench.run --backend gliner2 --suite all --device mps --out results/v1v2-gliner2.json
uv run python -m bench.run --backend laya --suite all --device mps --out results/v1v2-laya.json
```

Suite definitions: `bench/cases.py` (v1, frozen), `bench/cases_v2.py` (v2); registry in `bench/suites.py`.
Raw per-case records: `results/v1v2-{von,jev,gliner2,laya}.json`.
