# Head-to-head: Von (wfzyx/von-1.0) vs GLiNER2 (fastino/gliner2-large-v1) vs Laya (convaiinnovations/laya) vs Jev (typesafe/jev-1.13)

Benchmark: 8 tasks / 78 cases across three System One primitives —
**choice** (multi-class routing), **noul** (binary yes/no probability), **score** (ordered multi-level rating).
All four models answer the *same* question JSON (instructions + criteria) per case; Von, GLiNER2 and Laya run
locally on Apple MPS, Jev via OpenRouter's `/api/alpha/decisions` endpoint (same System One schema, no prompt
round-tripping, measured $0.00123 across all 87 requests — about $0.000014 per call).

Von numbers below are von-sdk **1.0.1** (commit b9e42b2), which added noul yes/no hypothesis synthesis,
a "How <adj>" lexical-bias fix in `rate`, fp16 on MPS, and ships `calibration.json` (temperature 1.1692,
applied automatically). The 1.0.0 runs are kept for comparison: `results/von.json`, `results/von-mps.json`
(micro 0.654 / macro 0.625).

## Scoreboard

| Task (type) | Von 1.0.1 | GLiNER2 | Laya | Jev |
|---|---|---|---|---|
| support_department (choice) | 0.867 | 0.933 | 0.533 | **1.000** |
| email_intent (choice) | **1.000** | 0.900 | 0.900 | **1.000** |
| refund_eligible (noul) | 0.700 | 0.500 | 0.700 | **1.000** |
| urgency (noul) | **1.000** | **1.000** | 0.875 | **1.000** |
| secret_leak (noul) | 0.875 | 0.500 | 0.500 | **1.000** |
| frustration_level (score) | **1.000** | **1.000** | 0.667 | **1.000** |
| incident_severity (score) | **1.000** | 0.556 | 0.444 | 0.778 |
| review_sentiment (score) | **1.000** | 0.889 | 0.333 | **1.000** |
| **micro accuracy** | 0.923 | 0.795 | 0.615 | **0.974** |
| **macro accuracy** | 0.930 | 0.785 | 0.619 | **0.972** |
| mean latency / case | ~54 ms | ~93 ms | **~48 ms** | ~302 ms |
| total wall time (78 cases) | 10.0 s | 20.3 s | 37.3 s † | 23.7 s |

† Laya's wall includes a one-time 33.6 s model load; per-case inference is post-warmup.

Ranking is now `Jev ≈ 0.974 > Von ≈ 0.923 > GLiNER2 ≈ 0.795 > Laya ≈ 0.615` — Laya owns the fastest
per-case clock (though with spikier p95, up to ~154 ms) and Von is close behind at 54 ms and far more
accurate. Accuracy is identical on CPU (`results/von-1.0.1-cpu.json`, `results/laya-cpu.json`),
only latency differs.

Records (on this suite):

- `results/von-1.0.1-mps.json` — `uv run python -m bench.run --backend von --device mps`
- `results/von-1.0.1-cpu.json` — `uv run python -m bench.run --backend von --device cpu`
- `results/gliner2-mps.json` — `uv run python -m bench.run --backend gliner2 --device mps`
- `results/laya-mps.json` — `uv run python -m bench.run --backend laya --device mps`
- `results/laya-cpu.json` — `uv run python -m bench.run --backend laya --device cpu`
- `results/jev.json` — `uv run python -m bench.run --backend jev` (needs `OPENROUTER_API_KEY` or `SANDBOX_OPENROUTER_API_KEY`)
- legacy 1.0.0: `results/von-mps.json`, `results/von.json`

## Von 1.0.1 — top local model; `judge`/`rate` fixed, misses are overconfident

The 1.0.0 failures ("flat ~0.5 noul, hard calm-bias on scores") are gone. All three score tasks are now
perfect with MAE 0.0 (`frustration_level` was 0.222), `urgency` went from AUC 0.44 to 1.00, and `secret_leak`
from all-decisions-wrong to 7/8. What's left is a small set of errors with high confidence:

- **Routing**: "The API returns a 500 error whenever we upload files larger than 10MB." → `other` 0.64
  (persisted from 1.0.0); "Our SSO integration with Okta started returning empty profiles…" → `account` 0.80
  (new — "profiles" lexically pulls toward account management).
- **refund_eligible false negatives at near-zero probability** (AUC 0.86 ranking is otherwise fine):
  "My annual subscription charge went through yesterday. I have not even created an account yet." → p 0.000;
  "It has been three weeks since checkout. We ended up not using the product…" → p 0.0001;
  "I bought this yesterday for a project that got cancelled…" → p 0.003. Mean |p − gold| = 0.30.
- **secret_leak**: "You can log in as admin with the password correct-horse-battery-staple." → p 0.39
  (below the 0.5 threshold); the other three credential states clear it.

Takeaway: 5.6× faster than Jev, free, and now within 5 points of it on micro accuracy — at 78 cases, the
remaining gap is roughly one to four decisions per task.

## GLiNER2 — now second among locals; keyword-driven and overconfident

Strong on social-language tasks: `urgency` 1.000 (AUC 1.0), `frustration_level` 1.000 (MAE 0.0),
`review_sentiment` 0.889. But it fails in a distinctive way: **mentions of policy keywords flood the
probability scale**, so near-saturated confidence (p ≈ 0.96–0.99) sits on *wrong* answers:

- **refund_eligible inverted (AUC 0.32)**: "My team has been using the product every day for the past eight
  months" → p(entitled) = 0.958; "plan activated fourteen weeks ago" → p = 1.000. Every "no" case is answered
  "yes" at ~max confidence.
- **secret_leak 0.500 yet AUC 1.0**: perfect *ranking*, broken decisions — all four no-secret states ("We
  rotate our access tokens every ninety days", "MQTT_PASSWORD was not set") get p(secret) = 0.84–0.99.
  The ordering information exists; the absolute scale is unusable.
- **incident_severity off-by-one from both ends**: a tagline typo → level 1; "notifications hours late" →
  level 2 (p = 0.94); yet "all customer data in the EU region has been permanently deleted" → level 3
  (p = 0.71) and platform-down → level 3.
- Small routing blips: "Can I book a demo of the enterprise features…" → `other` (0.74 vs sales 0.07);
  "Let's sync Monday morning… I will send an invite" → `fyi` at p = 0.999.

Takeaway: 13 points *behind* Von now, at 1.7× the latency. Its confidence values remain uncalibrated —
threshold tuning per task at best.

## Laya — fastest per-case clock, weakest decisions; hot-triggered, cool-graded

Laya natively speaks the same System One schema (its `Agent.system_one` batches all questions into one
forward pass over a ModernBERT-family encoder, ~421M params). It wins the `urgency` ordering (AUC 1.0)
and `email_intent` (0.900), and never misses a frustration level by more than one — but accuracy collapses
where other models hold up:

- **Support routing 0.533**: 8 of 15 cases misrouted, nearly everything pulled toward `billing`/`account`.
  "Can I book a demo of the enterprise features…" → `tech` 0.29 vs `sales` 0.26; the GDPR deletion request →
  `billing` 0.44 vs `account`; "Where is your office located?" → `billing`.
- **secret_leak: over-triggers like GLiNER2 but harsher** — all four no-secret states flagged `yes`
  (p 0.63–0.94; "MQTT_PASSWORD was not set" → 0.94). All four real credentials were caught, so AUC 0.81
  but coin-flip decisions.
- **review_sentiment 0.333 with a level-1 attractor**: positive reviews are graded cool —
  "Best gadget I have bought in years" → level 1 at p = 0.99, near-mechanical 0.97–0.99 confidence spikes
  on the wrong level for four of nine cases.
- **incident_severity 0.444** (MAE 0.78) — under-rates by one to two levels; `frustration_level` shows the
  same low bias but stays within ±1 (within_1 = 1.000).

Takeaway: the fastest local clock and pleasant ergonomics, but on this suite it trails old Von 1.0.0
(0.654) as well as GLiNER2 — the `billing`/`account` attractor in `choice` and mis-scaled `score`
probabilities need retraining-level fixes, not threshold tuning.

## Jev (typesafe) — decisively ahead, misses only severity boundary cases

18 of 20 task-cells perfect, including all `noul` tasks with clean separations (urgency AUC 1.0,
secret_leak AUC 1.0, refund correct in both directions) and `frustration_level` 9/9. The only misses are two
adjacent-level severity calls:

- "Push notifications are arriving several hours late" → 2 (expected 1), p(2) = 0.89.
- "Search results are stale until the user manually refreshes" → 1 (expected 2), p(1) = 0.78.

Residual caveats: probabilities are directionally right but not tight (mean |p − gold| = 0.23 on
`refund_eligible` despite perfect decisions), and being a hosted API it costs per call (~$0.000014, measured $0.00123 for 87 requests total) with
network-inclusive latency and occasional slow samples (p95 up to ~940 ms).

## Reproduce

```
uv run python -m bench.run --backend von --device mps --out results/von-1.0.1-mps.json
uv run python -m bench.run --backend gliner2 --device mps --out results/gliner2-mps.json
uv run python -m bench.run --backend laya --device mps --out results/laya-mps.json
uv run python -m bench.run --backend jev --out results/jev.json
```

Suite definitions with gold labels live in `bench/cases.py`; backends in `bench/backends/`
(one adapter per model, shared `Choice`/`Noul`/`Score` question schema).
