# Head-to-head: Von 1.2/1.1 (wfzyx/von) vs GLiNER2 (fastino/gliner2-large-v1) vs Laya (convaiinnovations/laya) vs Jev (typesafe/jev-1.13)

Benchmark: two hash-locked suites across three System One primitives —
**choice** (multi-class routing), **noul** (binary yes/no probability), **score** (ordered multi-level rating):

- **v1** — 8 tasks / 78 cases (`cases/v1.toml`), the original suite
- **v2** — 49 tasks / 866 cases (`cases/v2.toml`), extensions of every v1 question (same schema, all-new
  cases, ids suffixed `_v2`) plus new adjacent- and distant-domain tasks; no case overlap with v1

All four models answer the *same* question JSON (instructions + criteria) per case. Von, GLiNER2 and
Laya run locally on Apple MPS; Jev is hosted via OpenRouter's `/api/alpha/decisions` endpoint (same
System One schema, no prompt round-tripping, measured $0.00123 across the 87 v1 requests — about
$0.000014 per call, ~$0.013 per full 947-case run). All cases are synthetic, generated and
cross-checked by a committee of LLMs; debatable or ambiguous cases were removed before freezing
(details in [`cases/README.md`](../cases/README.md)).

Participants and records:

- **Von 1.2** (`wfzyx/von`) — same Option-Marker family as 1.1, retrained (von-sdk 1.2.2). Record:
  `results/von-1.2-mps.json` (locked 944 cases).
- **Von 1.1** (`wfzyx/von`) — Option-Marker joint-attention head on ModernBERT-large via von-sdk 1.1.1,
  fp16, input-conditioned calibration map. Record: `results/von-1.1-mps.json` (runs the locked
  866-case v2). Earlier Von rows are von-sdk 1.0.1 / the Berta NLI engine on `wfzyx/von-1.0`
  (scalar calibration T=1.1692): `results/historical/v1v2-von.json`,
  `results/historical/von-1.0.1-mps.json`, `results/historical/von-1.0.1-cpu.json`; legacy 1.0.0:
  `results/historical/von-mps.json`, `results/historical/von.json` (all indexed in
  [`historical/`](historical/README.md)).
- **Jev** (`typesafe/jev-1.13`) — `results/v1v2-jev.json`, `results/historical/jev.json`
- **GLiNER2** (`fastino/gliner2-large-v1`) — questions with parentheses are paraphrased for its schema
  compiler (adapter-level). Records: `results/v1v2-gliner2.json`, `results/historical/gliner2-mps.json`
- **Laya** (`convaiinnovations/laya`) — native System One schema. Records:
  `results/historical/v1v2-laya.json`, `results/historical/laya-mps.json`,
  `results/historical/laya-cpu.json`; Sep-2026 re-run: `results/laya-0.3.17-mps.json`
  (root English checkpoint, answers identical to `historical/v1v2-laya.json`) and
  `results/laya-typed-decisions-mps.json` (typed-decisions checkpoint).

† **Case-count caveat.** GLiNER2, Jev and the Von 1.0.x rows were recorded on the pre-lock v2
revision (869 cases). Three cases were removed before v2 was locked (dispositions in
[`cases/ISSUES.md`](../cases/ISSUES.md)); the affected task rows are marked † below. The scoreboards
re-derive those runs onto the locked cases (their answers to the removed cases are dropped), so
every column shares the same denominators — the historical analysis prose below retains the original
869-case figures where it discusses those runs. The Sep-2026 re-run records (Von 1.2, Laya 0.3.17
root and typed-decisions) are scored entirely on the locked suite. Probability metrics across the
Von 1.0.x ↔ 1.1 boundary are not comparable: 1.1+ reports input-conditioned, deliberately softer
probabilities where 1.0.x saturated near 0/1.

## Headline

| Record | v1 (78) | v2 (866) | combined (944) |
|---|---|---|---|
| Von 1.2 | 0.936 (0.927) | 0.724 (0.720) | 0.742 (0.749) |
| Von 1.1 | 0.936 (0.927) | 0.724 (0.720) | 0.742 (0.749) |
| Jev | **0.974** (**0.972**) | **0.967** (**0.969**) | **0.967** (**0.969**) |
| GLiNER2 | 0.795 (0.785) | 0.689 (0.684) | 0.698 (0.698) |
| Laya typed-decisions | 0.641 (0.642) | 0.624 (0.622) | 0.625 (0.624) |
| Laya root | 0.615 (0.619) | 0.585 (0.584) | 0.588 (0.589) |

micro (macro) accuracy, locked cases († runs re-derived — see caveat). Von 1.2 and Von 1.1 tie to
three decimals at every level despite 223 changed predictions: exactly 100 fixed and 100 broke
(case-level verified; see Analysis).

| | mean latency / case (v1+v2 run) | wall time |
|---|---|---|
| Laya (MPS) | **46 ms** | 76 s ‡ |
| Laya root 0.3.17 (MPS) | 50 ms | 50 s |
| Laya typed-decisions (MPS) | 50 ms | 52 s |
| Von 1.1 (MPS) | 53 ms | 55 s |
| Von 1.2 (MPS) | 56 ms | 58 s |
| GLiNER2 (MPS) | 73 ms | 80 s |
| Jev | ~330 ms | ~5.2 min |

‡ Laya's wall includes a one-time ~34 s model load; per-case inference is post-warmup. Jev latency is
network-inclusive with occasional slow samples (p95 up to ~940 ms). Von 1.1 per-suite means: 48 ms
(v1), 53 ms (v2), worst-task p95 111 ms — accuracy is identical on CPU (`results/historical/von-1.0.1-cpu.json`
pattern), only latency differs.

Robustness to the v2 shift (micro, v1 → v2): Jev −1.0 pt (0.974 → 0.964), Laya −3.1 (0.615 → 0.585),
GLiNER2 −10.7 (0.795 → 0.688), Von 1.1 −21.2 (0.936 → 0.724; Von 1.0.1 was −25.7). Jev remains the
only model that essentially ignores the domain shift; Von 1.1's slope improves on 1.0.1 but is still
the steepest of the four, and it now leads the locals on v2 outright instead of trading places with
GLiNER2. Re-run slopes: Von 1.2 is identical to 1.1 (−21.2), while Laya typed-decisions is now the
flattest of every record (−1.7, 0.641 → 0.624) and Laya root −3.0.

## v1 scoreboard (8 tasks / 78 cases)

| Task (type) | n | Von 1.2 | Von 1.1 | Jev | GLiNER2 | Laya-typed | Laya root |
|---|---|---|---|---|---|---|---|
| support_department (choice) | 15 | **1.000** | **1.000** | **1.000** | 0.933 | 0.667 | 0.533 |
| email_intent (choice) | 10 | **1.000** | **1.000** | **1.000** | 0.900 | 0.900 | 0.900 |
| refund_eligible (noul) | 10 | 0.900 | 0.900 | **1.000** | 0.500 | 0.400 | 0.700 |
| urgency (noul) | 8 | 0.875 | 0.625 | **1.000** | **1.000** | **1.000** | 0.875 |
| secret_leak (noul) | 8 | 0.750 | **1.000** | **1.000** | 0.500 | 0.500 | 0.500 |
| frustration_level (score) | 9 | **1.000** | **1.000** | **1.000** | **1.000** | 0.556 | 0.667 |
| incident_severity (score) | 9 | **1.000** | **1.000** | 0.778 | 0.556 | 0.667 | 0.444 |
| review_sentiment (score) | 9 | 0.889 | 0.889 | **1.000** | 0.889 | 0.444 | 0.333 |
| **micro accuracy** | 78 | 0.936 | 0.936 | **0.974** | 0.795 | 0.641 | 0.615 |
| **macro accuracy** | | 0.927 | 0.927 | **0.972** | 0.785 | 0.642 | 0.619 |

On v1 Von 1.1 trades its old perfection on `urgency`/`review_sentiment` for full marks on
`support_department`, `secret_leak` and `refund_eligible` — a wash in aggregate (micro 0.923 → 0.936,
macro 0.930 → 0.927).

## v2 scoreboard (49 tasks / 866 cases)

Extensions of the eight v1 questions first, then the new tasks in authoring order. † = task carried
a since-removed pre-lock case (see caveat); those runs are re-derived onto the locked cases here.

| Task (type) | n | Von 1.2 | Von 1.1 | Jev | GLiNER2 | Laya-typed | Laya root |
|---|---|---|---|---|---|---|---|
| support_department_v2 (choice) | 17 | 0.824 | 0.882 | **1.000** | 0.882 | 0.765 | 0.588 |
| email_intent_v2 (choice) | 15 | 0.733 | 0.867 | **1.000** | 0.800 | 0.800 | 0.733 |
| refund_eligible_v2 (noul) | 17 | 0.824 | 0.882 | **1.000** | 0.529 | 0.294 | 0.412 |
| urgency_v2 (noul) | 18 | 0.611 | 0.611 | **1.000** | **1.000** | 0.778 | 0.722 |
| secret_leak_v2 (noul) | 16 | 0.688 | 0.500 | **0.875** | 0.438 | 0.500 | 0.562 |
| frustration_level_v2 (score) | 18 | 0.889 | 0.833 | **0.944** | 0.667 | 0.722 | 0.500 |
| incident_severity_v2 (score) | 14 | 0.714 | 0.643 | **1.000** | 0.357 | 0.286 | 0.214 |
| review_sentiment_v2 (score) | 18 | 0.500 | 0.556 | **0.944** | 0.500 | 0.389 | 0.278 |
| expense_category (choice) | 18 | 0.944 | 0.944 | **1.000** | 0.778 | 0.889 | 0.778 |
| oncall_route (choice) | 17 | 0.824 | 0.824 | **1.000** | 0.882 | 0.765 | 0.824 |
| churn_risk (score) | 18 | 0.833 | 0.778 | **1.000** | 0.833 | 0.667 | 0.389 |
| lead_qualification (score) | 16 | 0.750 | 0.625 | **0.938** | 0.562 | 0.438 | 0.438 |
| app_review_intent (choice) | 16 | 0.812 | **1.000** | **1.000** | 0.938 | 0.938 | 0.938 |
| content_moderation (choice) | 18 | 0.667 | 0.556 | **1.000** | 0.611 | 0.778 | 0.722 |
| code_review_intent (choice) | 17 | 0.647 | 0.765 | **0.941** | 0.412 | 0.353 | 0.412 |
| commit_intent (choice) † | 15 | 0.733 | 0.667 | **1.000** | 0.533 | 0.867 | 0.800 |
| recipe_cuisine (choice) | 18 | 0.722 | 0.722 | **1.000** | 0.889 | 0.611 | 0.556 |
| question_duplicate (noul) | 16 | **1.000** | **1.000** | **1.000** | 0.500 | 0.625 | 0.688 |
| sql_injection_risk (noul) | 15 | 0.667 | 0.533 | **1.000** | 0.467 | 0.533 | 0.333 |
| travel_policy_violation (noul) | 17 | 0.647 | 0.588 | **1.000** | 0.647 | 0.647 | 0.588 |
| contains_pii (noul) | 17 | 0.588 | 0.824 | **0.941** | 0.765 | 0.824 | 0.765 |
| contains_spoiler (noul) | 16 | 0.562 | 0.625 | **0.938** | 0.562 | 0.500 | 0.500 |
| formality_level (score) | 16 | 0.500 | 0.438 | **0.938** | 0.562 | 0.312 | 0.188 |
| phishing_email (noul) | 17 | 0.471 | 0.529 | **1.000** | 0.882 | 0.706 | 0.647 |
| meeting_conflict (noul) | 17 | 0.471 | 0.412 | **1.000** | 0.529 | 0.471 | 0.471 |
| hazmat_shipping (noul) | 16 | 0.750 | 0.500 | **1.000** | 0.562 | 0.438 | 0.562 |
| dietary_vegan (noul) | 17 | 0.588 | 0.706 | **1.000** | 0.529 | 0.529 | 0.588 |
| news_topic (choice) | 17 | 0.882 | 0.882 | **1.000** | 0.941 | 0.706 | 0.765 |
| document_type (choice) | 15 | 0.733 | 0.733 | **1.000** | 0.800 | 0.733 | 0.733 |
| reading_level (score) | 16 | 0.500 | 0.562 | **1.000** | 0.500 | 0.500 | 0.375 |
| insurance_claim_priority (score) | 16 | 0.500 | 0.375 | **0.875** | 0.812 | 0.562 | 0.375 |
| symptom_triage (score) | 19 | **1.000** | **1.000** | 0.895 | 0.368 | 0.526 | 0.421 |
| delivery_exception (choice) | 19 | 0.895 | **1.000** | **1.000** | 0.947 | **1.000** | **1.000** |
| city_service_request (choice) | 19 | 0.947 | 0.947 | **1.000** | 0.895 | 0.842 | 0.737 |
| ad_policy_violation (noul) | 16 | 0.688 | 0.500 | **1.000** | 0.625 | 0.625 | 0.750 |
| fair_housing_violation (noul) † | 18 | 0.833 | 0.889 | **1.000** | 0.500 | 0.500 | 0.500 |
| contract_clause_type (choice) | 17 | 0.882 | 0.941 | **1.000** | 0.941 | 0.882 | 0.882 |
| voice_assistant_intent (choice) | 20 | 0.900 | 0.950 | **1.000** | 0.950 | 0.800 | 0.750 |
| grammar_issue (choice) † | 21 | 0.810 | **0.905** | 0.857 | 0.238 | 0.190 | 0.238 |
| action_item_assignment (noul) | 19 | 0.737 | 0.789 | **0.947** | 0.632 | 0.789 | 0.579 |
| suspicious_transaction (noul) | 17 | 0.471 | 0.529 | **1.000** | 0.529 | 0.471 | 0.588 |
| return_reason (choice) | 18 | 0.667 | 0.667 | **1.000** | 0.944 | 0.611 | 0.500 |
| allergen_present (noul) | 22 | 0.818 | 0.591 | **0.909** | 0.545 | 0.455 | 0.500 |
| home_service_routing (choice) | 23 | 0.957 | 0.913 | **1.000** | 0.957 | 0.870 | 0.826 |
| gaming_report_type (choice) | 20 | 0.700 | 0.700 | **0.900** | 0.750 | 0.800 | 0.750 |
| warranty_claim_eligible (noul) | 20 | 0.450 | 0.550 | **0.850** | 0.500 | 0.450 | 0.500 |
| weather_alert_severity (score) | 22 | 0.727 | 0.455 | 0.864 | **0.909** | 0.682 | 0.545 |
| content_type (choice) | 22 | 0.682 | 0.773 | **0.955** | 0.909 | 0.591 | 0.636 |
| veterinary_triage (score) | 20 | 0.550 | 0.800 | **0.950** | 0.700 | 0.450 | 0.450 |
| **micro accuracy** | 866 | 0.724 | 0.724 | **0.967** | 0.689 | 0.624 | 0.585 |
| **macro accuracy** | | 0.720 | 0.720 | **0.969** | 0.684 | 0.622 | 0.584 |

## Analysis

### Von 1.2 — 223 changed predictions, zero net, aimed at twists

Against Von 1.1 on identical cases (verified at case level): 223/944 predictions changed and they
cancel **exactly — 100 fixed, 100 broke**. The identical aggregates are coincidence, not caching.
The churn is aimed at the semantic-twist axis (re-cut in [`shape-knowledge.md`](shape-knowledge.md)):
accuracy on twist-heavy cases rose (T≥2 0.669 → 0.698, T3 0.400 → 0.450) and the
knowledge-light/twist-heavy quadrant gained +3.1 pts, while easy and knowledge-heavy cells gave some
back. Per operator: the boundary drop shrank −0.30 → −0.14 (0.46 → 0.60 — partially escaping the
chance cluster the other small models sit in) and the negation gap vanished (−0.10 → +0.01);
conflicting evidence is now its biggest remaining operator gap (−0.16) and the clearest shared gap
across the small models.

Task-level swings run both ways (≥5 correct): `weather_alert_severity` 10→16, `allergen_present`
13→18, `hazmat_shipping` 8→12 up; `veterinary_triage` 16→11, `contains_pii` 14→10 down. Score
placement improved (MAE 0.42 → 0.36) and v1 `urgency`'s threshold pathology self-healed (0.625 →
0.875 at AUC 1.000) — but two v2 noul tasks now rank *inverted* (`meeting_conflict` AUC 0.375,
`travel_policy_violation` 0.455); those are threshold/flip fixes, not comprehension failures. Noul
ordering still beats the 0.5 cut everywhere: AUC 0.752 vs acc 0.674, with per-task cuts recovering
to 0.828 (in-sample upper bound).

### Laya — root checkpoint unchanged; typed-decisions is the new model

The 0.3.17 root English checkpoint changed **0 of 944 predictions** versus the pre-lock record: the
update added subfolders (`multilingual/`, `typed-decisions/`), temperature validation (a clamp on
its out-of-range `choice:11+` bucket, flagged uncalibrated there) and plumbing — not decisions.

The `typed-decisions` checkpoint is the substantive new model: 0.625 combined (+3.7 over root) with
the flattest v1→v2 slope of any record (−1.7). Gains concentrate on routing and score placement
(`commit_intent` 0.867, `home_service_routing` 0.870, `churn_risk` 0.389 → 0.667,
`insurance_claim_priority` 0.375 → 0.562; score MAE 0.77 → 0.60 — the cool-grading attractor is
halved, not gone). Its sharper edge cuts both ways: perfect AUCs on `urgency`, `ad_policy_violation`
and `suspicious_transaction`, but strongly inverted ranking on `sql_injection_risk` (AUC 0.232) and
`refund_eligible_v2` (0.458); `grammar_issue` remains the family floor (0.190).

### Von 1.1 — the marker head largely closes the domain gap, but decisions got threshold-sensitive

What1.0.1's mode collapses were — and what happened to them:

- **`grammar_issue` 0.182 → 0.905** — the worst cell in the entire benchmark became one of Von's best
  (19/21; the only model above 0.3 on the task). The 1.0.x "everything is `subject_verb_agreement`"
  collapse is gone.
- **Rating scales stopped compressing downward**: `symptom_triage` 0.421 → 1.000 (MAE 0.95 → 0.00),
  `veterinary_triage` 0.450 → 0.800 (MAE 0.80 → 0.20), `frustration_level_v2` 0.556 → 0.833
  (MAE 0.44 → 0.17), `reading_level` 0.375 → 0.562 (MAE 0.88 → 0.50).
- **`commit_intent` 0.375 → 0.667** and **`question_duplicate` 0.750 → 1.000**; noul ranking improves
  nearly across the board (mean AUC 0.750 → 0.787): `refund_eligible_v2` 0.63 → 0.88,
  `warranty_claim_eligible` 0.42 → 0.71, `hazmat_shipping` 0.61 → 0.83.
- By type (v1+v2): choice 0.779 → 0.845, noul 0.630 → 0.659, score 0.614 → 0.686 (MAE 0.52 → 0.42).

What regressed or remains:

- **`urgency` is now thresholding, not ranking.** v1 `urgency` 1.000 → 0.625 and `urgency_v2`
  0.889 → 0.611, yet AUC stays 0.94 and 1.00 — every gold-yes still ranks above every gold-no. The
  yes-probabilities collapsed from 0.97–1.00 to 0.17–0.65 (no's sit at 0.04–0.22), so three of four
  v1 gold-yes land below the 0.5 cut at p = 0.17/0.27/0.34. Von 1.1 reports deliberately softer
  probabilities (input-conditioned calibration); where that softens toward the middle, the 0.5
  threshold is the wrong cut. If this shape appears in deployment, adjust the decision threshold —
  the ordering information is intact.
- **`insurance_claim_priority` 0.625 → 0.375** (MAE 0.38 → 0.88): errors scatter polarized rather
  than off-by-one — mid-level golds pulled to level 3 (1→3 ×3) or level 0 (1→0 ×3).
  `weather_alert_severity` 0.545 → 0.455 (MAE 0.55 → 0.91) and `incident_severity_v2` 0.786 → 0.643
  show the same looser level placement (errors like 3→1).
- **Choice regressions on some routing tasks**: `oncall_route` 1.000 → 0.824, `content_moderation`
  0.722 → 0.556, `recipe_cuisine` 0.833 → 0.722, `gaming_report_type` 0.800 → 0.700.
- v1 misses are now four decisions: the three `urgency` threshold misses plus one `review_sentiment`
  level (2→3 at p3 0.70).

Config note: from 1.1 the adapter forwards noul `criteria` (true/false descriptions) to the model —
1.0.x runs dropped them — and the checkpoint ships an input-conditioned calibration map. Accuracy
deltas above therefore mix model and wiring changes; probability columns are not comparable across
the boundary.

### Jev — 31 errors in the 869-case v2 run, all small and near-boundary

- Over-flags on two binary tasks with borderline "no" cases: `secret_leak_v2` and `contains_pii`
  (also `action_item_assignment`, `allergen_present` ×2) — `yes` on states that discuss tokens,
  identifiers, or assignments without containing one.
- Adjacent-level severity/rating misses: `weather_alert_severity` (0→1, 1→3 twice),
  `insurance_claim_priority` (1→2, 1→0), `symptom_triage` (3→2, 0→1), `formality_level` 3→2,
  `veterinary_triage` 1→0.
- Near-synonym category confusions in choice: `gaming_report_type` smurfing→cheating, boosting→other;
  `code_review_intent` nit→refactor; `commit_intent` refactor→chore; `content_type`
  feature→news_report.
- `warranty_claim_eligible` is its weakest task (0.850, three yes→no).
- The one v1 cell it loses is `incident_severity` (0.778 vs Von's 1.000 — the same two adjacent-level
  boundary cases listed in [`cases/ISSUES.md`](../cases/ISSUES.md)); those cases do not recur on the
  `incident_severity_v2` extension (Jev 1.000), so it is not a systematic Von advantage.
- Probabilities are directionally right but not tight (mean |p − gold| = 0.23 on `refund_eligible`
  despite perfect decisions); as a hosted API it costs per call and shows occasional slow samples
  (p95 up to ~940 ms).

### GLiNER2 — keyword-driven and overconfident, but the flattest non-Jev slope

- Strong on social-language tasks: `urgency_v2` 1.000 (where Von 1.1's threshold problem bites),
  `weather_alert_severity` 0.909 (best of the four), `insurance_claim_priority` 0.812 (best of the
  locals), `phishing_email` 0.882, `return_reason` 0.944, `voice_assistant_intent` 0.950,
  `home_service_routing` 0.957; on v1 `urgency`/`frustration_level` are perfect and `review_sentiment`
  0.889.
- Its distinctive failure: **mentions of policy keywords flood the probability scale**, so
  near-saturated confidence (p ≈ 0.84–1.00) sits on wrong answers. `refund_eligible` is inverted
  (AUC 0.32): "using the product every day for the past eight months" → p(entitled) 0.958;
  "plan activated fourteen weeks ago" → p 1.000. `secret_leak` v1: 0.500 accuracy with AUC 1.0 —
  perfect ordering, unusable scale (all four no-secret states get p(secret) 0.84–0.99).
- The same mode persists on v2 material: `secret_leak_v2` 0.438 (over-flags discussion of tokens),
  `sql_injection_risk` 0.467, `grammar_issue` 0.227, `incident_severity_v2` 0.357 and `symptom_triage`
  0.368 (both worse than Von), `incident_severity` v1 off-by-one from both ends (tagline typo →
  level 1; data permanently deleted → level 3).
- Its slope is flatter than Von's (−10.7 vs −21.2 v1→v2 micro) but Von 1.1 now beats it on v2 micro
  outright (0.724 vs 0.688; under Von 1.0.1 the ranking was reversed). Extension tasks that are easy
  for Von's v1 get harder for it (`frustration_level_v2` 0.667 vs 1.000 on v1; `review_sentiment_v2`
  0.500 vs 0.889) while its weak cells stay weak — hence flatter, lower macro on v2 than its micro
  suggests. Confidence values remain uncalibrated — threshold tuning per task at best.

### Laya (0.3.x) — fastest per-case clock, weakest decisions; hot-triggered, cool-graded

- Laya natively speaks the System One schema (one forward pass over a ModernBERT-family encoder,
  ~421M params) and stays nearly flat across the shift (0.615 → 0.585) — but from last place.
- The **cool-grading attractor** dominates every rating task: `formality_level` 0.188 (worst cell of
  the four models), `incident_severity_v2` 0.214, `review_sentiment_v2` 0.278, v1
  `incident_severity` 0.444 (MAE 0.78) and `review_sentiment` 0.333 ("Best gadget I have bought in
  years" → level 1 at p 0.99) — most misses stay within one level (`within_1` 0.88/0.93/0.67 on the
  three worst), with near-mechanical 0.97–0.99 confidence spikes on the wrong level.
- The **`billing`/`account` attractor** in choice: v1 support routing 0.533 ("Can I book a demo of the
  enterprise features…" → `tech` 0.29 vs `sales` 0.26; GDPR deletion request → `billing`; "Where is
  your office located?" → `billing`).
- `secret_leak` over-triggers like GLiNER2 but harsher — all four no-secret states flagged
  ("MQTT_PASSWORD was not set" → p 0.94) while all four real credentials were caught (AUC 0.81,
  coin-flip decisions).
- Genuine highlights: `delivery_exception` 1.000 (ties Jev and Von 1.1), `commit_intent` 0.812
  (second only to Jev — it reads commit messages better than Von does), `content_moderation` 0.722 /
  `ad_policy_violation` 0.750 (both above Von 1.1), and the best noul *ordering* of the locals on
  `hazmat_shipping` (AUC 0.92 vs GLiNER2 0.68 and Von 1.1 0.83, against 0.56 accuracy — ranking is
  real, the 0.5 threshold just doesn't know it).

## Version history (Von)

- **1.0.0** (`results/historical/von-mps.json`, `results/historical/von.json`) — micro 0.654 / macro 0.625 on v1; flat ~0.5
  noul probabilities and a hard calm-bias on scores.
- **1.0.1** (`wfzyx/von-1.0`, Berta NLI engine, scalar calibration T=1.1692) — added noul yes/no
  hypothesis synthesis and a "How <adj>" lexical-bias fix in `rate`; v1 micro 0.923 / macro 0.930,
  but off its training distribution it mode-collapsed (`grammar_issue` 0.182, `commit_intent` 0.375,
  downward-compressed rating scales) with overconfident near-zero misses on `refund_eligible`.
- **1.1** (`wfzyx/von`, Option-Marker joint attention, input-conditioned calibration) — v1
  0.936 / 0.927, v2 0.724 / 0.720. The mode collapses are largely gone (see analysis); probabilities
  are honest and softer, which makes 0.5-threshold decisions sensitive on unfamiliar criteria
  (`urgency`).
- **1.2** (`wfzyx/von`, von-sdk 1.2.2) — same family retrained: v1 0.936 / 0.927, v2 0.724 / 0.720 —
  aggregates identical to 1.1 through exactly offsetting churn (100 fixed / 100 broke of 223 changed
  predictions). The churn is concentrated on twist-heavy cases and the boundary/negation operators
  (see analysis and [`shape-knowledge.md`](shape-knowledge.md)); score MAE 0.42 → 0.36.

## Version history (Laya)

- **0.3.x root** (`results/historical/v1v2-laya.json`, `results/historical/laya-mps.json`,
  `results/historical/laya-cpu.json`) — root English checkpoint, the original rows above.
- **0.3.17 root** (`results/laya-0.3.17-mps.json`) — decision-identical to the 0.3.x record (0/944
  predictions changed); adds `multilingual/` and `typed-decisions/` checkpoints and temperature
  validation (clamping an out-of-range `choice:11+` entry).
- **0.3.17 typed-decisions** (`results/laya-typed-decisions-mps.json`) — 0.625 combined (+3.7 over
  root), flattest v1→v2 slope of any record (−1.7), cool-grading halved (score MAE 0.77 → 0.60).

## Takeaway

Jev is still decisively ahead (combined 0.967) and generalizes to suitably out-of-domain tasks
essentially unchanged (−1.0 pt micro across 869 new cases), at ~6× the latency and a fraction of a
cent per 1k calls. Von 1.2 remains the best local model (combined 0.742 vs GLiNER2's 0.698 and Laya
typed-decisions' 0.625) and ties Von 1.1 in aggregate while handling semantic twists measurably
better (see analysis and [`shape-knowledge.md`](shape-knowledge.md)); it still needs threshold care
where its softened probabilities cross 0.5. Between Laya checkpoints, typed-decisions is the one to
ship (+3.7 and the flattest shift slope). The local models fail in signatures that are easy to detect
in production: Von with mid-scale probability mass on unfamiliar criteria and occasional inverted
noul ranking (ordering mostly intact), GLiNER2 with saturated confidence on trigger words, Laya root
with a compressed rating scale that reads cool on everything.

## Reproduce

```bash
uv run python -m bench.run --backend von --device mps --suite all --out results/von-1.1-mps.json
uv run python -m bench.run --backend von --device mps --suite all --out results/von-1.2-mps.json
uv run python -m bench.run --backend jev --suite all --out results/v1v2-jev.json
uv run python -m bench.run --backend gliner2 --device mps --suite all --out results/v1v2-gliner2.json
uv run python -m bench.run --backend laya --device mps --suite all --out results/historical/v1v2-laya.json
uv run python -m bench.run --backend laya --device mps --suite all --out results/laya-0.3.17-mps.json
uv run python -m bench.run --backend laya --device mps --suite all --laya-path models/convaiinnovations/laya/typed-decisions --out results/laya-typed-decisions-mps.json
```

Suite definitions with gold labels: `cases/v1.toml`, `cases/v2.toml` (both hash-locked; registry in
`bench/suites.py`, schema in `bench/cases.py`, one adapter per model in `bench/backends/`).
Raw per-case records: `results/*.json` (each carries `suite_summaries` per suite plus the combined
`summary`). `results/benchmark-summary.md` and `results/v1v2-summary.md` are symlinks to this file,
kept so older links keep working.