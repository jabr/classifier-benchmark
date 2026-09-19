# Head-to-head: Von (wfzyx/von-1.0) vs GLiNER2 (fastino/gliner2-large-v1) vs Jev (typesafe/jev-1.13)

Benchmark: 8 tasks / 78 cases across three System One primitives —
**choice** (multi-class routing), **noul** (binary yes/no probability), **score** (ordered multi-level rating).
All three models answer the *same* question JSON (instructions + criteria) per case; Von and GLiNER2 run locally
on Apple MPS, Jev via OpenRouter's `/api/alpha/decisions` endpoint (same System One schema, no prompt
round-tripping, measured $0.00123 across all 87 requests — about $0.000014 per call).

## Scoreboard

| Task (type) | Von | GLiNER2 | Jev |
|---|---|---|---|
| support_department (choice) | 0.933 | 0.933 | **1.000** |
| email_intent (choice) | **1.000** | 0.900 | **1.000** |
| refund_eligible (noul) | 0.500 | 0.500 | **1.000** |
| urgency (noul) | 0.625 | 1.000 | **1.000** |
| secret_leak (noul) | 0.500 | 0.500 | **1.000** |
| frustration_level (score) | 0.222 | 1.000 | **1.000** |
| incident_severity (score) | 0.556 | 0.556 | **0.778** |
| review_sentiment (score) | 0.667 | 0.889 | **1.000** |
| **micro accuracy** | 0.654 | 0.795 | **0.974** |
| **macro accuracy** | 0.625 | 0.785 | **0.972** |
| mean latency / case | **~62 ms** | ~93 ms | ~302 ms |
| total wall time (78 cases) | 10.7 s | 20.3 s | 23.7 s |

Records (on this suite; accuracy does not change on CPU, only latency):

- `results/von-mps.json` — `uv run python -m bench.run --backend von --device mps`
- `results/gliner2-mps.json` — `uv run python -m bench.run --backend gliner2 --device mps`
- `results/jev.json` — `uv run python -m bench.run --backend jev` (needs `OPENROUTER_API_KEY` or `SANDBOX_OPENROUTER_API_KEY`)

## Von — fastest, weakest; `judge`/`rate` barely read the input

Von's `decide` (choice) earns its keep: `email_intent` 10/10 and one miss in support routing (a literal
"API returns a 500 error" ticket routed to `other` 0.32 vs `tech` 0.23). The binary and rating primitives are
another story — they look largely content-insensitive:

- **urgency inverted**: "Checkout is completely down and we are losing sales every minute. Help ASAP." →
  p(urgent) = 0.206. The social-media-outage case scores 0.310; AUC 0.438 (worse than chance ordering).
- **secret_leak**: all four states containing real credentials ("API_KEY=sk-test-…", `-----BEGIN RSA PRIVATE
  KEY-----`, admin password) scored below threshold (p 0.33–0.49). Ranking is somewhat usable (AUC 0.75) but
  every decision is wrong.
- **refund_eligible wrong in both directions**: p(no) = 0.43 for "I bought this yesterday… nothing was ever
  used", while "consulting package fully delivered last month" gets p(refund) = 0.53. Chance-level AUC 0.54.
- **frustration_level 0.222 with a hard calm-bias**: all three angry cases rated level 0 — including
  "Your garbage app destroyed three hours of work. Fix it NOW." (p(calm) = 0.47) and "STOP billing my card."
  Meanwhile a polite thank-you ("Thanks a lot for the fast update…") drifts to level 1.
- **Severe down-shift on incident_severity**: "The entire platform has been unreachable for all customers for
  the past hour" → level 2/4; "minutes to load each page" → level 0.
- **Sentiment extremes collapse**: "Absolutely love this. Best gadget I have bought in years" → 1-star,
  p = 0.46.

Takeaway: Von is 5× faster than Jev and free, but its headline primitives beyond `choice` are unreliable —
the `test-von.py` "beats Jev" claim does not survive this suite (−32 accuracy points).

## GLiNER2 — best local model, but keyword-driven and overconfident

Strong on some social-language tasks Von fails outright: `urgency` 1.000 (AUC 1.0), `frustration_level`
1.000 (MAE 0.0), `review_sentiment` 0.889. But it fails in a distinctive way: **mentions of policy keywords
flood the probability scale**, so near-saturated confidence (p ≈ 0.96–0.99) sits on *wrong* answers:

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

Takeaway: the strongest local option (14 points over Von at only 1.5× the latency), but treat its confidence
values as uncalibrated — routing decisions on `noul`/`score` need threshold tuning per task at best.

## Jev (typesafe) — decisively ahead, misses only severity boundary cases

18 of 20 task-cells perfect, including all `noul` tasks with clean separations (urgency AUC 1.0,
secret_leak AUC 1.0, refund both directions correct where both local models are at 0.500) and
`frustration_level` 9/9. The only misses are two adjacent-level severity calls:

- "Push notifications are arriving several hours late" → 2 (expected 1), p(2) = 0.89.
- "Search results are stale until the user manually refreshes" → 1 (expected 2), p(1) = 0.78.

Residual caveats: probabilities are directionally right but not tight (mean |p − gold| = 0.23 on
`refund_eligible` despite perfect decisions), and being a hosted API it costs per call (~$0.000014, measured $0.00123 for 87 requests total) with
network-inclusive latency and occasional slow samples (p95 up to ~940 ms).

## Reproduce

```
uv run python -m bench.run --backend von --device mps --out results/von.json
uv run python -m bench.run --backend gliner2 --device mps --out results/gliner2.json
uv run python -m bench.run --backend jev --out results/jev.json
```

Suite definitions with gold labels live in `bench/cases.py`; backends in `bench/backends/`
(one adapter per model, shared `Choice`/`Noul`/`Score` question schema).
