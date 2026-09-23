# Shape vs. knowledge: what actually decides these cases

Sidecar study answering one question: when the local models miss, is it **problem shape** (semantic
twists and decision rules — trainable with targeted data) or **world knowledge** (facts not carried
in the state — trainable with domain data)? Every locked case (944) was annotated blind along two
independent axes, and the recorded runs in `results/*.json` were re-cut along them.

- Annotations + rubric: [`cases/annotations/`](../cases/annotations/README.md) (`shape-knowledge.jsonl`,
  shared-set votes in `agreement.json`)
- Re-cut tool: `bench/strata.py` (`uv run python -m bench.strata`) — pure analysis over recorded
  numbers; no model is run and no suite is touched
- Annotators: six LLM annotators (MiMo V2.6 Pro sub-agents), each covering a disjoint set of tasks
  plus the same shared 24-case reliability set, **blind to `results/`** — annotation cannot be
  biased toward known model errors

Axes: **twist** (0–3: semantic work between state and gold — direct → bridge → one operator
(negation, exception, boundary arithmetic, distractor, attribution) → interacting operators or
conflicting evidence) and **knowledge** (0–3: background facts beyond state + criteria — none →
everyday → professional literacy → specialist). Plus `crux` (which component decides the label:
direct / composition / decision / knowledge), `tags` (which twist operators are load-bearing), and
`unreachable` (gold not derivable — the `cases/README.md` bright line).

## Reliability

Six-way agreement on the shared 24 cases (360 annotator pairs): twist exact 0.58, knowledge exact
0.70, `crux` exact 0.77 — but **within-1 agreement 0.99** on both ordinal scales (mean |diff| 0.43
/ 0.31). All disagreement is ±1 boundary fuzz, which is why every analysis below bins to low (0–1)
vs high (2–3). Validity checks: one annotator flagged `v1:incident_severity:4` ("stale search
results until manually refreshed" — gold requires "no easy workaround", the state names one) as
`unreachable` **from the rubric alone**, independently matching its `cases/ISSUES.md` disposition;
the shared-set sibling `v1:incident_severity:5` drew 1/6 `unreachable` votes, itself evidence that
the bright line is genuinely fuzzy there. Exactly one `unreachable` in the merged file.

## What the suites contain

| twist | n | | knowledge | n | | crux | n |
|---|---|---|---|---|---|---|---|
| 0 | 246 | | 0 | 474 | | direct | 372 |
| 1 | 370 | | 1 | 320 | | composition | 308 |
| 2 | 308 | | 2 | 148 | | decision | 98 |
| 3 | 20 | | 3 | 2 | | knowledge | 166 |

Tags: distractor 159, implicit 102, boundary 48, conflict 36, negation 28, paraphrase 23,
**attribution 4, exception 4, coref 3**. The suites are twist-rich but operator-narrow: attribution,
exception and coreference are barely exercised — a coverage gap for any future suite or corpus.

## Finding 1 — twist predicts everyone's errors; knowledge mostly predicts GLiNER2's

Accuracy by twist (monotone for all four):

| twist | n | Von 1.1 | Jev | GLiNER2 | Laya |
|---|---|---|---|---|---|
| 0 | 246 | 0.825 | **1.000** | 0.760 | 0.724 |
| 1 | 370 | 0.765 | **0.973** | 0.738 | 0.559 |
| 2 | 308 | 0.669 | **0.938** | 0.627 | 0.532 |
| 3 | 20 | 0.400 | **0.900** | 0.300 | 0.300 |

Quadrants (low = 0–1, high = 2–3):

| stratum | n | Von 1.1 | Jev | GLiNER2 | Laya |
|---|---|---|---|---|---|
| K low × T low | 535 | 0.793 | **0.989** | 0.781 | 0.639 |
| K low × T high | 259 | 0.676 | **0.942** | 0.622 | 0.533 |
| K high × T low | 81 | 0.765 | **0.951** | 0.519 | 0.531 |
| K high × T high | 69 | 0.565 | **0.913** | 0.551 | 0.464 |

Holding knowledge low, raising twist costs Von 11.7 pts (0.793 → 0.676); holding twist low, raising
knowledge costs it **2.8 pts** (0.793 → 0.765). GLiNER2 is the mirror image: knowledge costs it 26.2
pts where twist costs 15.9. Von 1.0.1 was knowledge-sensitive (0.761 → 0.494); the 1.1 marker head
largely removed that. Reading: Von 1.1 already *tolerates* knowledge load when the semantics are
clean — its gap is shape. That is the vessel thesis, supported with one inversion: the part of
"shape" that hurts most is not only semantic composition (Finding 3).

## Finding 2 — where each model's errors live

| model | errors | in T≥2 | in K≥2 | in K low × T high |
|---|---|---|---|---|
| Von 1.1 | 244 | 0.47 | 0.20 | 0.34 |
| Jev | 31 | 0.68 | 0.32 | 0.48 |
| GLiNER2 | 285 | 0.45 | 0.25 | 0.34 |
| Laya | 389 | 0.41 | 0.19 | 0.31 |

Exposure baselines: T≥2 is 35% of cases, K≥2 23%, K low × T high 27%. So Von's errors
**over-index** on twist (1.35×) and **under-index** on knowledge (0.87×) — the same for the other
locals. Even Jev's 31 residuals are twist-concentrated (68% in T≥2, 1.38× its exposure): semantic
twists are the universal residual difficulty, which makes twist data the highest-leverage corpus
for every model but Jev.

## Finding 3 — three error buckets, three different remedies

By `crux` (the component that decides the label):

| crux | n | Von 1.1 | Jev | GLiNER2 | Laya |
|---|---|---|---|---|---|
| direct | 372 | 0.83 | **1.00** | 0.79 | 0.72 |
| composition | 308 | 0.71 | **0.96** | 0.69 | 0.54 |
| decision | 98 | 0.66 | **0.89** | 0.56 | 0.42 |
| knowledge | 166 | 0.64 | **0.95** | 0.58 | 0.48 |

Von's 244 errors split by quadrant into three buckets with different fixes:

1. **Decision form — 111 errors (45%)**, the largest bucket, mostly in the *easy* quadrant (T0×K0
   alone: Von 0.82 vs Jev 1.00 on 202 trivial cases; `crux: decision` cells: Von 0.66, Laya 0.42).
   Comprehension is fine; the aggregation rule is wrong — 0.5 cuts on softened probabilities,
   level placement on ordinal scales, prior attractors. Much of this needs no new training data at
   all (Finding 5).
2. **Semantic composition — 84 errors (34%)** in K low × T high. This is the spine-corpus target.
3. **Knowledge — 49 errors (20%)** in K≥2 cells. Smallest bucket *by suite design* — the suites lean
   toward carrying facts in the state (84% of cases are K≤1), so this bucket is under-exposed here
   and will dominate in knowledge-heavy deployments. Fine-tuning on domain data is the tool.

Operator-level (accuracy with tag vs without — tags overlap, effects are marginal, not controlled):

| tag | n | Von 1.1 Δ | Jev Δ | GLiNER2 Δ | Laya Δ |
|---|---|---|---|---|---|
| boundary | 48 | **−0.30** | −0.01 | −0.23 | −0.09 |
| conflict | 36 | **−0.22** | −0.08 | −0.09 | −0.24 |
| implicit | 102 | **−0.16** | −0.01 | −0.05 | −0.23 |
| negation | 28 | −0.10 | −0.01 | +0.09 | −0.13 |
| paraphrase | 23 | −0.09 | +0.03 | −0.09 | −0.16 |
| distractor | 159 | −0.01 | −0.06 | **−0.17** | +0.02 |

The counter-intuitive result: **distractors do not hurt Von 1.1 at all** (0.75 tagged vs 0.74
untagged) — the marker head matches criteria, not keywords. What hurts Von is **boundary
arithmetic, conflicting evidence, and implied-but-unstated facts**; implied and conflicting evidence
hurt all three locals. GLiNER2 alone is distractor-clobbered (its keyword signature), and Jev's
largest tag drop is distractors too (−0.06) — its only visible weakness.

## Finding 4 — score placement is not where the twist damage lands

MAE on score tasks by twist: Von 1.1 0.40 (T 0–1) → 0.49 (T 2–3); Jev 0.05 → 0.14; GLiNER2 0.47 →
0.42; Laya 0.77 → 0.77. Von's level placement degrades little with twist — the twist slope lives in
choice (0.930 → 0.724) and noul (0.750 → 0.638). Laya's flat 0.77 is its cool-grading attractor:
absolute placement error, indifferent to the case.

## Finding 5 — a large part of the decision bucket is free

Noul ordering vs threshold (all 337 noul cases):

| model | AUC | acc @0.5 | best global cut | acc @best | best per-task cut (in-sample) |
|---|---|---|---|---|---|
| Von 1.1 | 0.753 | 0.659 | 0.24 | 0.688 | **0.816** |
| Jev | 0.994 | 0.970 | 0.52 | 0.976 | 1.000 |
| GLiNER2 | 0.690 | 0.602 | 0.99 | 0.632 | 0.694 |
| Laya | 0.708 | 0.579 | 0.17 | 0.677 | **0.769** |
| Von 1.0.1 | 0.705 | 0.632 | 0.08 | 0.682 | 0.712 |

The `urgency` pathology generalizes: ordering beats the 0.5 cut on every local model. Per-task
threshold fitting (in-sample upper bound) recovers **+15.7 pts** of noul accuracy for Von 1.1 and
+19.0 for Laya without touching a weight. GLiNER2 recovers least (+9.2) — its saturation is an
ordering problem, not a cut problem. Von 1.0.1's saturated probabilities were less recoverable
(+8.0): 1.1's softer probabilities are more *usable*, even where they cost raw accuracy.

## Implications for a training corpus

The original plan — enumerate logical spines over twist operators, then realize semantic diversity
around them — is the right shape of solution, with the priorities revised by these numbers:

- **Prioritize the operators that actually bite**: boundary arithmetic (dates, counts, ≥/>, windows),
  conflicting evidence (two spans pushing different answers, resolved by scope/strength), implied
  facts (qualifying fact never stated), negation scope. Distractors are already well covered by the
  suites and Von is immune; include them for coverage (they punish keyword matchers) but don't make
  them the bulk.
- **Fill the coverage gaps**: attribution ("claims it is X"), exceptions ("unless/except"), and
  long-range coreference appear in 4/4/3 suite cases respectively — a spine generator can enumerate
  exactly these.
- **Don't expect the corpus to fix bucket 1.** Decision form wants calibration-aware training
  targets (soft labels derived from evidence strength — parameterizable in a spine), rubric-anchored
  level training for score, and per-task threshold fitting as the zero-training stopgap. A corpus
  alone will leave ~45% of Von's current errors untouched.
- **The knowledge bucket stays for domain fine-tuning** — and the clean test of "vessel quality"
  remains the sample-efficiency curve: shape-pretrained vessel + N domain rows vs. domain-only.

## Caveats

- Tag and knowledge cells are small (boundary 48, conflict 36, negation 28, paraphrase 23) and tags
  overlap; tag deltas are marginal associations, not controlled effects.
- Annotations are same-model (MiMo sub-agents): they measure context noise (±1 fuzz, hence the
  binning), not model-family bias in what counts as "specialist knowledge". One annotator consulted
  `cases/ISSUES.md` for the `unreachable` reference type (possible leakage on the two documented v1
  cases); the `v1:incident_severity:4` flag was independently produced by an annotator that read
  nothing but the rubric.
- Per-task threshold numbers are in-sample upper bounds; held-out fits would land lower.
- The knowledge bucket is under-exposed by suite construction (facts lean into the state), so the
  20% share is a floor for real deployments, not a ceiling.

Reproduce: `uv run python -m bench.strata` (tables above), `cases/annotations/agreement.json`
(shared-set votes). Model records: `results/von-1.1-mps.json`, `results/v1v2-{jev,gliner2,laya,von}.json`
(pre-lock † index drift folded back via `bench/strata.py`'s `PRELOCK_DROP`).