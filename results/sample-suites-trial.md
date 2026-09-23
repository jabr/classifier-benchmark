# First third-party sample benchmarks (trial run)

Preliminary results against the `sources/` sample suites — the first benchmark
runs on externally-sourced data with capped input lengths (≤120 words).
Suite composition and label-quality caveats are documented in
[`sources/README.md`](../sources/README.md). All four samples in this trial
draw from the two third-party synthetic generators (Support-Ticket Router,
TriageIQ). These samples are scratch artifacts (seed-family `04d2` /
seed 1234, git-ignored); the recorded numbers below are the point of record.

Samples run, all with backends **von**, **jev** (`typesafe/jev-1.13`),
**gliner2** (large), **laya**, on MPS. Von was later re-run on the same cases with
Von 1.1 (Option-Marker); both generations are shown below:

| Sample | n | Primitive | Classes | Raw records |
|---|---|---|---|---|
| `support_tickets-04d2` (test split) | 500 | choice | 6 routes | `results/support_tickets-0492.json` |
| `triageiq-04d2` | 100 | choice | 5 triage classes | `results/triageiq-0492.json` |
| `triageiq_negative-04d2` | 100 | noul | negative vs not | `results/triageiq_negative-0492.json` |
| `triageiq_urgency-04d2` | 100 | score | 3-level urgency | `results/triageiq_urgency-0492.json` |

Percentages are micro accuracy (macro equals micro here: single-task suites,
balanced or near-balanced classes).

Von 1.1 re-run record (all four samples in one file): `results/sample-04d2-run2.json`.

## Headline

| Sample | Jev | GLiNER2 | Von 1.0.1 (berta) | Von 1.1 (marker) | Laya |
|---|---|---|---|---|---|
| support_tickets routing (n=500) | **0.978** | 0.856 | 0.860 | 0.818 | 0.590 |
| triageiq category (n=100) | **0.910** | 0.700 | 0.660 | 0.720 | 0.720 |
| triageiq_negative (n=100, noul) | 0.840 | 0.710 | 0.810 | 0.740 | **0.860** |
| triageiq_urgency (n=100, score) | **0.590** | 0.550 | 0.540 | 0.530 | 0.420 |

Von 1.0.1 → Von 1.1 on identical cases (expected sequence verified state-for-state):
category **+6 pts** (0.660 → 0.720), routing −4.2 (0.860 → 0.818), negative −7
(0.810 → 0.740), urgency flat (0.540 → 0.530) — micro 0.789 → 0.760 overall. The
failure *shapes* move more than the aggregates (see the Von 1.1 re-run section).

Mean latency (p95), measured via the harness:

| Backend | routing (n=500) | category | negative | urgency |
|---|---|---|---|---|
| von 1.1 (marker) | **58 ms (63)** | **53 (59)** | **35 (42)** | **47 (52)** |
| von 1.0.1 (berta) | 101 ms (112) | 90 (99) | 37 (42) | 55 (61) |
| jev | 297 ms (476) | 279 (434) | 346 (457) | 269 (373) |
| gliner2 | 380 ms (406) | 333 (355) | 212 (225) | 315 (329) |
| laya | 61 ms (64) | 56 (62) | 38 (44) | 47 (52) |

## Findings

1. **Jev leads everywhere, with routing as the standout.** 0.978 on the 500-case
   ticket router is the highest accuracy recorded anywhere in this project;
   even its worst class (`upgrade`) is 78/84.

2. **On ticket routing, Von 1.0.1 ≈ GLiNER2 with different failure modes.**
   0.860 vs 0.856 overall, but the errors differ: Von 1.0.1's concentration on
   developer questions (`api → billing` 20, `api → technical`
   18 — `api` is its worst class at 44/83), while GLiNER2 confuses
   `api → technical` (30) and misfires on `upgrade → billing` (24). Both
   suggest hand-rolled "developer intent" cues are the hard part of routing
   synthetic SaaS tickets.

3. **Laya is wildly uneven — the fastest local model is also the noul winner.** It
   posts the highest accuracy on the negative-sentiment noul (0.860, beating
   Jev) with the best true-negative rate (41/50), while collapsing on the
   6-way router (0.590, three-quarters of its errors funnel into `billing`) and on
   `other` in the category task (2/20). At 38–61 ms mean it is 5–8x faster
   than GLiNER2, and like all local models here it is free — Jev is the only
   paid backend in the project. For binary detection workloads it
   deserves a permanent slot; for flat routing it is a hazard.

4. **Von 1.0.1's noul is over-sensitive to "yes".** Perfect 50/50 true-positive rate
   on negative sentiment, but true negatives only 31/50 (AUC 0.910, so
   threshold tuning would recover most of it — same shape as its earlier
   `secret_leak` behavior). Jev's AUC 0.977 at a 0.5 threshold shows what a
   calibrated yes/no boundary buys.

5. **Urgency is a level-boundary problem, not a signal problem.** Every model
   struggles on exact 3-level hits (0.42–0.59), yet within-1 accuracy is
   0.90–1.00: adjacent levels are being confused, zero not at all. Von 1.0.1,
   GLiNER2, and Laya systematically under-call high urgency (`2 → 1`: 15, 14,
   25 occurrences); Jev drifts the other way (`1 → 0`: 16). Consistent with
   the generation-assigned urgency labels being soft at boundaries — worth
   remembering before treating this suite as a knife-edge score test.

## Von 1.1 re-run (Option-Marker)

`results/sample-04d2-run2.json`, same 800 cases (expected sequence identical to the
trial records), von-sdk 1.1.1 on MPS. Versus Von 1.0.1 per class:

- **Routing 0.860 → 0.818 — a new `complaint` attractor.** `complaint` goes perfect
  (76/84 → 84/84) but now pulls everything toward it: `api → complaint` 20,
  `upgrade → complaint` 11, `technical → complaint` 11, `billing → complaint` 8.
  `upgrade` collapses (78/84 → 64/84); `api` remains the worst class (40/83,
  `api → technical` 23). The 1.0.1 attractor was `billing` (`api → billing` 20) —
  that confusion is gone, replaced rather than fixed.
- **Category 0.660 → 0.720 — real gain, same blind spot.** `other` 11/20 → 16/20 and
  `account` 16/20 → 18/20 drive it. `feature_request` is still the broken class
  (5/20 → 4/20; `feature_request → other` x13 — the 1.0.1 signature at x8, stronger).
- **Negative noul 0.810 → 0.740 — softer and leakier both ways.** The 1.0.1
  yes-bias persists (`no → yes` 19 → 20 of 50) but now also leaks the other
  direction (`yes → no` 6 of 50; TPR 50/50 → 44/50, TNR 31/50 → 30/50).
  AUC 0.910 → 0.871, mean |p − gold| 0.209 → 0.319: the softer probabilities
  that help elsewhere hurt at the 0.5 cut here.
- **Urgency 0.540 → 0.530 — the level-0 bug fixed, the drift direction flipped.**
  Level-0 recall 4/33 → 20/33 (`0 → 1` x27 → x12) — 1.0.1's upward bias is gone —
  but the model now grades cool overall (mean level bias +0.16 → −0.20;
  `2 → 1` x15 → x18, `1 → 0` x13). Exact 0.540 → 0.530, within-1 0.98 → 0.97,
  MAE 0.48 → 0.50. Still a level-boundary problem, per finding 5.
- **1.3–1.7× faster per case** (58/53/35/47 ms vs 101/90/37/55) — the marker head
  now has the fastest local clock on every sample.

Net: one clear win (category), one clear loss (negative), one replaced failure mode
(routing), one wash with better shape (urgency).

## Caveats

- One seed-family per source, one run per backend; treat deltas < ~5pts as
  noise at n=100. More seeds are cheap to generate (`just gen <source>`).
- The two ticket datasets are synthetic (generation-assigned labels — see
  `sources/README.md`). The project's one real-human-text source (cfpb) was
  not exercised here; it carries self-reported labels requiring screening
  before use.
- Model row provenance: Von 1.0.1 = released `wfzyx/von-1.0` weights, berta engine
  (von-sdk `14d0987`); Von 1.1 = `wfzyx/von`, Option-Marker (von-sdk 1.1.1). The
  vendor's own README numbers for the option-marker variant were not reproducible
  from the earlier released artifact (marker measured here at 0.659 micro / 0.672
  macro across v1+v2 vs their claimed 71.5% macro on v2); the von-1.1 re-release
  does reproduce them (v2 macro 0.720 — see `benchmark.md`).

## Reproduce

Generate the exact samples (each deterministic from its seed):

```bash
just gen support_tickets   --seed 1234 --n 500
just gen triageiq          --seed 1234 --n 100
just gen triageiq_negative --seed 1234 --n 100
just gen triageiq_urgency  --seed 1234 --n 100
```

Run the sweep (one JSON per sample):

```bash
uv run python -m bench.run --sample support_tickets-04d2,triageiq-04d2,triageiq_negative-04d2,triageiq_urgency-04d2 \
  --backend von,jev,gliner2,laya --out results/<name>.json
```

Von 1.1 re-run (all four samples in one file):

```bash
uv run python -m bench.run --sample support_tickets-04d2,triageiq-04d2,triageiq_negative-04d2,triageiq_urgency-04d2 \
  --backend von --device mps --out results/sample-04d2-run2.json
```
