# Von vs Jev — full suite (v1 + v2), 947 cases

Head-to-head of two System One decision models across both test suites: **v1** (8 tasks / 78 cases,
`bench/cases.py`) and **v2** (49 tasks / 869 cases, `bench/cases_v2.py`). No case overlap between suites.

**Status:** v2 results are preliminary — shared with the Von project for review before being promoted
to the headline comparison in the README.

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

- **Von 1.0.1** (`wfzyx/von-1.0`), local ModernBERT on Apple MPS, fp16, calibrated T=1.1692
- **Jev** (`typesafe/jev-1.13`), hosted via OpenRouter `/api/alpha/decisions`, one request per case
  (~$0.013 total for 947 requests at ~$0.000014/call)

The v1 block reproduces the earlier recorded runs exactly (Von 0.923 micro, Jev 0.974 micro — see
`benchmark-summary.md` for the four-model comparison including GLiNER2 and Laya).

## Headline

| Suite | n | Von micro | Von macro | Jev micro | Jev macro |
|---|---|---|---|---|---|
| v1 | 78 | 0.923 | 0.930 | **0.974** | **0.972** |
| v2 | 869 | 0.666 | 0.667 | **0.964** | **0.966** |
| **combined** | 947 | 0.687 | 0.704 | **0.965** | **0.967** |

| | mean latency / case | wall time (947 cases) |
|---|---|---|
| Von (MPS) | **55 ms** | **57 s** |
| Jev | ~330 ms | ~5.2 min |

The five-point gap on v1 becomes a thirty-point gap on v2. Jev loses barely a point going from v1 to
v2; Von drops from 0.923 to 0.666 — and the drop is not just the new domains: on the eight *extension*
tasks (same questions, new states from the same domains as v1) Von averages 0.718 where v1 gave it
0.923, while Jev averages 0.970 on those same extension tasks.

## v1 (8 tasks / 78 cases)

| Task (type) | n | Von | Jev |
|---|---|---|---|
| support_department (choice) | 15 | 0.867 | **1.000** |
| email_intent (choice) | 10 | **1.000** | **1.000** |
| refund_eligible (noul) | 10 | 0.700 | **1.000** |
| urgency (noul) | 8 | **1.000** | **1.000** |
| secret_leak (noul) | 8 | 0.875 | **1.000** |
| frustration_level (score) | 9 | **1.000** | **1.000** |
| incident_severity (score) | 9 | **1.000** | 0.778 |
| review_sentiment (score) | 9 | **1.000** | **1.000** |

## v2 (49 tasks / 869 cases)

First the eight extensions of v1 questions, then the new tasks in authoring order.

| Task (type) | n | Von | Jev |
|---|---|---|---|
| support_department_v2 (choice) | 17 | 0.765 | **1.000** |
| email_intent_v2 (choice) | 15 | 0.800 | **1.000** |
| refund_eligible_v2 (noul) | 17 | 0.647 | **1.000** |
| urgency_v2 (noul) | 18 | 0.889 | **1.000** |
| secret_leak_v2 (noul) | 16 | 0.688 | **0.875** |
| frustration_level_v2 (score) | 18 | 0.556 | **0.944** |
| incident_severity_v2 (score) | 14 | 0.786 | **1.000** |
| review_sentiment_v2 (score) | 18 | 0.611 | **0.944** |
| expense_category (choice) | 18 | 0.833 | **1.000** |
| oncall_route (choice) | 17 | **1.000** | **1.000** |
| churn_risk (score) | 18 | 0.778 | **1.000** |
| lead_qualification (score) | 16 | 0.625 | **0.938** |
| app_review_intent (choice) | 16 | 0.875 | **1.000** |
| content_moderation (choice) | 18 | 0.722 | **1.000** |
| code_review_intent (choice) | 17 | 0.706 | **0.941** |
| commit_intent (choice) | 16 | 0.375 | **0.938** |
| recipe_cuisine (choice) | 18 | 0.833 | **1.000** |
| question_duplicate (noul) | 16 | 0.750 | **1.000** |
| sql_injection_risk (noul) | 15 | 0.533 | **1.000** |
| travel_policy_violation (noul) | 17 | 0.647 | **1.000** |
| contains_pii (noul) | 17 | 0.706 | **0.941** |
| contains_spoiler (noul) | 16 | 0.562 | **0.938** |
| formality_level (score) | 16 | 0.438 | **0.938** |
| phishing_email (noul) | 17 | 0.471 | **1.000** |
| meeting_conflict (noul) | 17 | 0.529 | **1.000** |
| hazmat_shipping (noul) | 16 | 0.438 | **1.000** |
| dietary_vegan (noul) | 17 | 0.471 | **1.000** |
| news_topic (choice) | 17 | 0.941 | **1.000** |
| document_type (choice) | 15 | 0.800 | **1.000** |
| reading_level (score) | 16 | 0.375 | **1.000** |
| insurance_claim_priority (score) | 16 | 0.625 | **0.875** |
| symptom_triage (score) | 19 | 0.421 | **0.895** |
| delivery_exception (choice) | 19 | 0.895 | **1.000** |
| city_service_request (choice) | 19 | 0.947 | **1.000** |
| ad_policy_violation (noul) | 16 | 0.562 | **1.000** |
| fair_housing_violation (noul) | 19 | 0.684 | **0.947** |
| contract_clause_type (choice) | 17 | 0.941 | **1.000** |
| voice_assistant_intent (choice) | 20 | 0.900 | **1.000** |
| grammar_issue (choice) | 22 | 0.182 | **0.864** |
| action_item_assignment (noul) | 19 | 0.842 | **0.947** |
| suspicious_transaction (noul) | 17 | 0.529 | **1.000** |
| return_reason (choice) | 18 | 0.611 | **1.000** |
| allergen_present (noul) | 22 | 0.591 | **0.909** |
| home_service_routing (choice) | 23 | 0.913 | **1.000** |
| gaming_report_type (choice) | 20 | 0.800 | **0.900** |
| warranty_claim_eligible (noul) | 20 | 0.450 | **0.850** |
| weather_alert_severity (score) | 22 | 0.545 | **0.864** |
| content_type (choice) | 22 | 0.636 | **0.955** |
| veterinary_triage (score) | 20 | 0.450 | **0.950** |

## What breaks, in which way

**Von — mode collapse and trigger drift off its training distribution:**

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

**Jev — 31 errors in 869 cases, all small and near-boundary:**

- Over-flags on two binary tasks with borderline "no" cases: `secret_leak_v2` and `contains_pii`
  (also `action_item_assignment`, `allergen_present` ×2) — `yes` on states that discuss tokens,
  identifiers, or assignments without containing one.
- Adjacent-level severity/rating misses: `weather_alert_severity` (0→1, 1→3 twice), `insurance_claim_priority`
  (1→2, 1→0), `symptom_triage` (3→2, 0→1), `formality_level` 3→2, `veterinary_triage` 1→0.
- Near-synonym category confusions in choice: `gaming_report_type` smurfing→cheating, boosting→other;
  `code_review_intent` nit→refactor; `commit_intent` refactor→chore; `content_type` feature→news_report.
- `warranty_claim_eligible` is its weakest task (0.850, three yes→no).

**The one place Von beats Jev on v1** is `incident_severity` (1.000 vs 0.778) — the same two
adjacent-level boundary cases Jev misses there disappear on the small `incident_severity_v2` extension
(Jev 1.000), so it isn't a systematic Von advantage, just lenient level placement.

## Takeaway

Jev generalizes to suitably out-of-domain tasks essentially unchanged (−1 point micro across 869 new
cases); Von's 1.0.1 gains hold only where states look like its training data. At ~6× the latency and a
fraction-of-a-cent per 1k calls, Jev remains the accuracy candidate; Von remains the fast local
baseline whose risky cells (grammar/ratings/unfamiliar binary criteria) are easy to detect — its errors
are concentrated mode-collapses, not scattered noise.

## Reproduce

```
uv run python -m bench.run --backend von --suite all --device mps --out results/v1v2-von.json
uv run python -m bench.run --backend jev --suite all --out results/v1v2-jev.json
```

Suite definitions: `bench/cases.py` (v1, frozen), `bench/cases_v2.py` (v2); registry in `bench/suites.py`.
Raw per-case records: `results/v1v2-von.json`, `results/v1v2-jev.json`.
