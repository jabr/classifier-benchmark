# First third-party sample benchmarks (trial run)

Preliminary results against the `sources/` sample suites — the first benchmark
runs on externally-sourced data with capped input lengths (≤120 words).
Suite composition and label-quality caveats are documented in
[`sources/README.md`](../sources/README.md). All four samples in this trial
draw from the two third-party synthetic generators (Support-Ticket Router,
TriageIQ). These samples are scratch artifacts (seed-family `04d2` /
seed 1234, git-ignored); the recorded numbers below are the point of record.

Samples run, all with backends **von**, **jev** (`typesafe/jev-1.13`),
**gliner2** (large), **laya**, on MPS:

| Sample | n | Primitive | Classes | Raw records |
|---|---|---|---|---|
| `support_tickets-04d2` (test split) | 500 | choice | 6 routes | `results/support_tickets-0492.json` |
| `triageiq-04d2` | 100 | choice | 5 triage classes | `results/triageiq-0492.json` |
| `triageiq_negative-04d2` | 100 | noul | negative vs not | `results/triageiq_negative-0492.json` |
| `triageiq_urgency-04d2` | 100 | score | 3-level urgency | `results/triageiq_urgency-0492.json` |

Percentages are micro accuracy (macro equals micro here: single-task suites,
balanced or near-balanced classes).

## Headline

| Sample | Jev | GLiNER2 | Von (berta) | Laya |
|---|---|---|---|---|
| support_tickets routing (n=500) | **0.978** | 0.856 | 0.860 | 0.590 |
| triageiq category (n=100) | **0.910** | 0.700 | 0.660 | 0.720 |
| triageiq_negative (n=100, noul) | 0.840 | 0.710 | 0.810 | **0.860** |
| triageiq_urgency (n=100, score) | **0.590** | 0.550 | 0.540 | 0.420 |

Mean latency (p95), measured via the harness:

| Backend | routing (n=500) | category | negative | urgency |
|---|---|---|---|---|
| von | 101 ms (112) | 90 (99) | 37 (42) | 55 (61) |
| jev | 297 ms (476) | 279 (434) | 346 (457) | 269 (373) |
| gliner2 | 380 ms (406) | 333 (355) | 212 (225) | 315 (329) |
| laya | 61 ms (64) | 56 (62) | 38 (44) | 47 (52) |

## Findings

1. **Jev leads everywhere, with routing as the standout.** 0.978 on the 500-case
   ticket router is the highest accuracy recorded anywhere in this project;
   even its worst class (`upgrade`) is 78/84.

2. **On ticket routing, von ≈ GLiNER2 with different failure modes.**
   0.860 vs 0.856 overall, but the errors differ: Von's concentration on
   concentration on developer questions (`api → billing` 20, `api → technical`
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

4. **Von's noul is over-sensitive to "yes".** Perfect 50/50 true-positive rate
   on negative sentiment, but true negatives only 31/50 (AUC 0.910, so
   threshold tuning would recover most of it — same shape as its earlier
   `secret_leak` behavior). Jev's AUC 0.977 at a 0.5 threshold shows what a
   calibrated yes/no boundary buys.

5. **Urgency is a level-boundary problem, not a signal problem.** Every model
   struggles on exact 3-level hits (0.42–0.59), yet within-1 accuracy is
   0.90–1.00: adjacent levels are being confused, zero not at all. Von,
   GLiNER2, and Laya systematically under-call high urgency (`2 → 1`: 15, 14,
   25 occurrences); Jev drifts the other way (`1 → 0`: 16). Consistent with
   the generation-assigned urgency labels being soft at boundaries — worth
   remembering before treating this suite as a knife-edge score test.

## Caveats

- One seed-family per source, one run per backend; treat deltas < ~5pts as
  noise at n=100. More seeds are cheap to generate (`just gen <source>`).
- The two ticket datasets are synthetic (generation-assigned labels — see
  `sources/README.md`). The project's one real-human-text source (cfpb) was
  not exercised here; it carries self-reported labels requiring screening
  before use.
- Model row provenance: von = released `wfzyx/von-1.0` weights, berta engine
  (von-sdk `14d0987`). The vendor's own README numbers for the option-marker
  variant are not reproducible from the released artifact (marker measured here
  at 0.659 micro / 0.672 macro across v1+v2 vs their claimed 71.5% macro on v2).

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
