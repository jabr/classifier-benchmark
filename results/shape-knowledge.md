# Zero-shot decision models: the small-encoder approach vs. a generative baseline

A zero-shot decision classifier receives its question at inference time — instructions plus criteria
in the System One wire shape, over three primitives: **choice** (multi-class routing), **noul**
(binary yes/no probability), **score** (ordered multi-level rating) — and must answer against
arbitrary states. Nothing about the task is fixed at training time. The question here is what that
demands, and how much of it a ~400M-parameter BERT-base-class encoder can master.

Three approaches are in evidence over 944 annotated benchmark cases and the recorded runs on them:

- **Decision encoders** — BERT-base-class encoders (~400–420M) with semantic-logic (NLI-style)
  fine-tuning and a learned decision head over the wire schema. Two class members studied.
- **Matchers** — GLiNER-style span/label grounding: score state spans against criteria labels and
  read the scores as decisions.
- **Generative baseline** — a hosted frontier model (Jev), answering the same wire schema. Treated
  as the reference for what unrestricted reasoning buys, not as a contender.

Evidence base: case annotations (twist/knowledge demand, deciding component, load-bearing operators
— rubric in [`cases/annotations/`](../cases/annotations/README.md)), the recorded runs re-cut along
them (`bench/strata.py`), and externally sourced sample suites as fresh-material cross-check
([`sample-suites-trial.md`](sample-suites-trial.md)). One decision-encoder subject had trained on
this repo's cases; knowledge-axis claims below rest on clean members only (method note).

## What zero-shot decisions demand

| demand | measure | n |
|---|---|---|
| **Composition** — semantic work between state and gold: paraphrase gaps, negation, exceptions, boundary arithmetic, distractors, implied facts, conflicting evidence | twist ≥ 2 | 328 (35%) |
| **Decision form** — applying the aggregation rule: thresholding a probability, placing an ordinal level, breaking near-ties | `crux: decision` | 98 (10%) |
| **Knowledge** — background facts neither state nor criteria carry | knowledge ≥ 2 | 150 (16%) |

Most of the hard cases are knowledge-*light*: 259 of the 328 twist-heavy cases sit at knowledge ≤1,
and the suites lean toward carrying their facts in the state (84% knowledge ≤1). Knowledge findings
are therefore floors for real deployments, not ceilings. Load-bearing operators, by frequency:
distractor 159, implicit 102, boundary 48, conflict 36, negation 28, paraphrase 23 — and
**attribution 4, exception 4, coref 3**: question-only zero-shot benchmarks barely exercise
attributed mentions ("the reporter claims…"), exception clauses, and long-range coreference at all.

## Semantic composition: learnable in the class, and the frontier's residual

Accuracy falls monotonically with twist for every approach — this is the axis that separates them:

| twist | n | matcher | decision encoders | baseline |
|---|---|---|---|---|
| 0 | 246 | 0.76 | 0.72 – 0.83 | **1.00** |
| 1 | 370 | 0.74 | 0.56 – 0.77 | **0.97** |
| 2 | 308 | 0.63 | 0.53 – 0.67 | **0.94** |
| 3 | 20 | 0.30 | 0.30 – 0.40 | **0.90** |

Composition skill is **trainable and it transfers**. Within the encoder class, the member with the
stronger semantic-logic fine-tuning gains +0.17…+0.22 over the weaker one precisely on the
NLI-shaped operators — paraphrase, implied facts, negation scope, conflicting evidence — the
competences NLI-style training is about. A ~400M encoder can learn to unwind semantic twists; that
is the core feasibility result for this class.

Two hard limits:

- **Boundary arithmetic is outside the class today.** On cases where dates, counts, or ≥/>-thresholds
  decide the answer, every member of both small classes collapses to chance (0.46–0.50) against its
  own 0.59–0.76 baseline — and within the encoder class the fine-tuning edge *vanishes* there
  (−0.04). The baseline is unbothered (0.96). Whatever the class's recipes install, date/count
  reasoning is not in it. This is the single sharpest class ceiling visible in the data.
- **Composition is also the baseline's residual.** The frontier model's rare misses are 68%
  twist-concentrated (≈2× their exposure) — interacting operators and conflicting evidence are the
  universal residual difficulty. Composition data is the one training data that raises every boat.

## Decision form: a design problem, not a data problem

The decision layer — not comprehension — is where the small classes lose the most recoverable
accuracy. On binary tasks, every small-class model **orders cases better than it thresholds them**:

| approach | noul AUC | acc @ 0.5 | best per-task cut (in-sample) | recoverable |
|---|---|---|---|---|
| matcher | 0.690 | 0.602 | 0.694 | +9 pts |
| decision encoders | 0.708 – 0.753 | 0.579 – 0.659 | 0.769 – 0.816 | **+10 – 20 pts** |
| baseline | 0.994 | 0.970 | 1.000 | ~0 |

In-sample per-task threshold fits — no training, no weights — recover up to ~20 points of binary
accuracy in the encoder class. The same signature shows on the other primitives: on
comprehension-easy but rule-hard cases (`crux: decision`) the *within-class spread is the largest of
any stratum* (0.42 – 0.66), and score placement errors run at MAE 0.42 vs 0.77 between class
members while barely reacting to twist. How the head maps evidence to a cut or an ordinal bin is a
first-order design choice — worth more than a large amount of training data.

Implication for the class: treat calibration as a component. Per-task threshold fitting is the
zero-training stopgap; training-side, soft targets derived from evidence strength (explicit mention
> paraphrase > implied > attributed) teach the probability axis instead of patching it, and
rubric-anchored bins teach level placement.

## Knowledge: the axis the class cannot fake

For the clean class members, knowledge demand costs about as much as semantic twist does — 10–26
points off their knowledge-light/twist-light base, with the matcher class most fragile (−26). The
baseline is nearly flat on both axes and leads 3 of 4 fresh external samples. No architecture trick
in either small class substitutes for facts: this is where "pour domain knowledge in" is the only
remedy, and where the *vessel* framing is the right positioning for the class — train for shape,
fine-tune per domain, and judge the result by the **sample-efficiency curve on post-training
material** (shape-trained vessel + N domain rows vs. domain-only), not by zero-shot general scores.

One caution the data makes vivid: knowledge exposure in training is invisible to evaluation on the
same distribution. A subject that has absorbed the benchmark's specific world knowledge appears
immunity-fluent on knowledge-heavy cases it has seen, with no corresponding general capability.
Knowledge claims for this class must be measured on material that postdates training — fresh-seeded
samples from external datasets are the design this repo already ships for exactly that.

## The matcher approach: the wrong inductive bias for decisions

Matchers degrade earlier and differently. Their failure is not missing subtlety but **mention ≠
satisfaction**: lexical triggers flood the confidence scale, so near-saturated confidence sits on
wrong answers (binary ordering sometimes perfect while the probability scale is unusable — e.g.
0.500 accuracy at AUC 1.0), and distractor cases are the one operator family that specifically
clobbers them (−0.17) — precisely the failure the encoder-class matching head design eliminates for
free. They are knowledge-sensitive (−26) and decision-layer-fragile (threshold recovery only +9).
On clean, trigger-friendly material they are competitive (fresh routing sample: 0.86), which is the
trap — their inductive bias matches lexical overlap, and zero-shot decision questions are written to
be answered by criterion satisfaction. Keep the class for extraction and candidate generation, not
for decisions.

## What follows for the small-model program

1. **Positioning: vessels, not generalists.** The realistic product is a shape-specialized encoder
   — strong composition, calibrated decision head — with domain knowledge fine-tuned in per
   deployment. The zero-shot-*general* gap to the baseline is structural (boundary arithmetic,
   facts), not a matter of more of the same training.
2. **Composition corpora are the highest-leverage training data** (they move the class's trainable
   axis and are the baseline's residual too). Generator design: enumerate logical spines — labeled
   logical forms whose gold is known by construction — and realize semantic diversity around them.
   Operator priorities from the damage evidence: **boundary first** (the class ceiling; nothing in
   current recipes covers it), then conflicting evidence, implied facts, negation scope; fill the
   **coverage gaps** the benchmark barely tests (attribution, exceptions, coreference); distractors
   secondary (the technique already handles them).
3. **Design the decision layer, don't hope for it.** Per-task thresholds now; evidence-strength soft
   labels and rubric-anchored ordinal targets in training. The largest within-class quality spread
   of any stratum sits here.
4. **Evaluation hygiene is part of the method.** Two-axis case annotation (composition vs knowledge)
   is cheap and separates trainable-shape errors from missing-facts errors; fresh post-training
   material is mandatory for knowledge claims; and gold labels must survive the screening line —
   a model matching an indefensible gold is evidence of exposure, not of reasoning.

## Method note

Annotations: 944 locked cases, six blind annotators (no access to model outputs), pairwise agreement
on a shared 24-case set — exact 0.58/0.70 on the two ordinal scales, **within-1 0.99** (all noise is
±1 boundary fuzz, hence low/high binning); raw votes in `cases/annotations/agreement.json`.
Re-cut tool: `uv run python -m bench.strata` (per-subject tables), `PRELOCK_DROP` there folds
pre-lock index drift back onto locked order.

Control logic: one decision-encoder subject trained on these cases, so its knowledge numbers cannot
distinguish absorbed benchmark facts from general competence, and its other numbers are upper
bounds. Class conclusions therefore (a) rest knowledge claims on the clean members, (b) treat
within-class fine-tuning contrasts as provisional in magnitude but sound in operator *pattern*
(corroborated by the clean member's damage profile), and (c) cross-check on external sample suites,
where the class edge over the clean member is heterogeneous (−0.12 to +0.23; +0.14 micro) and the
knowledge-heavy cells remain untested — the decisive missing measurement is knowledge-heavy fresh
material (e.g. `just gen cfpb`, post-training seeds).

Other caveats: per-task threshold figures are in-sample upper bounds; operator deltas are marginal
associations over overlapping tags (cells of 23–159 cases), not controlled effects; sample-suite
labels are generation-assigned and noisy.

Recorded subjects: `results/von-1.1-mps.json`, `results/v1v2-laya.json` (decision encoders),
`results/v1v2-gliner2.json` (matcher), `results/v1v2-jev.json` (baseline);
`results/sample-04d2-run2.json` and `results/*-0492.json` (fresh-material cross-check).