# Semantic variations on a spine

Training-data generator for von/laya-style decision encoders (~400M, System One wire shape:
`choice` / `noul` / `score`). Core principle: **gold by construction, semantics as controlled
variation**. Every item comes from a labeled logical form — a *spine* — whose answer an
interpreter computes; "semantic variation" is a set of operators with *label contracts*, so
surface diversity never costs label correctness. The benchmark's failure taxonomy becomes the
generator's operator taxonomy.

Why this shape of data (evidence in [`results/shape-knowledge.md`](../../results/shape-knowledge.md)):

- **Composition is the trainable axis** for the class, and the frontier model's residual too —
  interacting operators (boundary arithmetic, conflicting evidence first) are where every
  approach still loses.
- **Decision form is a design problem**: small models order cases better than they threshold
  them (+10–22 points recoverable per-task on noul). Soft targets that encode evidence strength
  teach the probability axis instead of patching it.
- Template/label shortcuts are the standing failure mode of decision heads (criterion keywords
  driving answers, fixed option labels driving `noul`). The generator treats shortcut-freedom as
  a gated property, not a hope.
- The screening rules of [`cases/README.md`](../../cases/README.md) (one defensible gold,
  realistic states, balanced classes, difficulty earned by reasoning) become **mechanical
  constraints** here rather than a review step.

## Layout

| File | Contents |
|---|---|
| `spine.py` | spine algebra + interpreter: `World`/`Statement` (with epistemic status), rule forms `Compare`/`Holds`/`Not`/`And`/`Or`/`Unless`, conflict resolution policies, noisy-reader soft targets |
| `realize.py` | operator catalog with label contracts, rendering demands, and the twist/knowledge/crux mapping (operationalizes [`cases/annotations/README.md`](../../cases/annotations/README.md)) |
| `generate.py` | the first family end to end (boundary eligibility), checks/gates, JSONL emitter |

```bash
uv run python -m training.spines.generate --self-test        # rubric-mapping expectations
uv run python -m training.spines.generate --n 3 --seed 1234 --out spines.jsonl
uv run python -m training.spines.generate --format kv --out spines-kv.jsonl
```

`--n` is per (domain x variant x **label**) cell: the default grid (2 domains x 8 variants) yields
96 items at `n=3`, balanced 50/50 by construction.

## The spine

A spine is (world, rule, question). Facts are `Statement`s carrying an **epistemic status** — the
operator's contract lives here: `asserted` (stated flatly), `verified` (authoritative source),
`paraphrased` (non-obvious wording), `inferred` (implied only, with inference depth), `claimed`
(attributed claim — *claim != fact*: it never establishes a property and enters as rival
evidence). Multiple statements on one key require an explicit conflict policy (`verified` /
`ranked` / `recent`) — conflicts must never be resolved implicitly.

The interpreter (`interpret`) returns gold, the evidence trace (support + rivals), and the
noisy-reader soft target:

```
strength = min(support strengths) x conflict decisiveness x boundary margin factor
p(yes)   = strength if gold else 1 - strength          (floored at 0.50, capped at 0.97)
```

| component | schedule | rationale |
|---|---|---|
| evidence strength | verified .97, asserted .95, paraphrased .90, inferred .80 − .10/extra step (floor .50), claimed .60 | explicit mention > paraphrase > implied > attributed |
| conflict decisiveness | explicit priority rule .85, heuristic (`recent`) .70 | weighing evidence is the twist-3 demand |
| boundary margin | .50 + .50·min(1, margin/near), `near` = 7 days here | near-boundary judgment calls interpolate toward a coin flip |
| floor .50 | weak-evidence items train toward *uncertainty*, never against their gold | |

These numbers are hyperparameters, not law: ablate soft vs hard targets per corpus.

## Operators and contracts

| operator | weight | label contract | priority (benchmark damage) |
|---|---|---|---|
| `boundary` | heavy | gold via date/count/threshold arithmetic; margin parameterized | **first** — class sits at chance (0.46–0.50) here |
| `conflict` | conflict | two sources disagree; the spine's resolution policy decides | **first** — clearest shared gap (−0.16…−0.24) |
| `implicit` | bridge | gold via inference chain (depth counted in epi) | high (102 cases) |
| `negation` | heavy | gold gates on stated absence or negation scope | high (28; demonstrably trainable) |
| `exception` | heavy | an `unless` clause selects the case class | gap-fill (only 4 benchmark cases test it) |
| `attribution` | heavy | claim != fact | gap-fill (4) |
| `coref` | bridge | gold preserved; references must be tracked | gap-fill (3) |
| `distractor` | heavy | gold preserved; near-miss / keyword decoy present | secondary (159; class already handles it) |
| `paraphrase` | bridge | gold preserved; non-obvious wording gap | standard |

**Rendering demand** matters as much as the operator: the same rule reads differently when the
measure is a stated number (plain comparison), two calendar dates (exact arithmetic), "about six
weeks ago" (unit arithmetic + fuzz), or "early June" (register + fuzz). The rendering selects the
statement's epistemic status (`number` → asserted; `dates`/`relative` → inferred depth 1; `vague`
→ depth 2), so difficulty and soft targets move together automatically.

## Free annotations

Every record carries `twist`/`knowledge`/`tags`/`crux` in the sidecar schema of
[`cases/annotations/README.md`](../../cases/annotations/README.md), computed from the operator
trace — no annotators, and training runs get `bench/strata`-style re-cuts for nothing. The
mapping (`realize.py`) is checked against the rubric's four calibration examples by
`--self-test`. Known limit: tags are *declared* from the applied operators; the mechanical
load-bearingness audit (flip the operator's fluent, gold must change) is on the roadmap.

## Gold defensibility and the gates

- **Unpinned-realization reject.** A rendering's reader-side imprecision (its `fudge` in days,
  plus display rounding error) must fit strictly *inside* the item's margin to the threshold, or
  the item is never emitted. Near-boundary judgment calls are therefore only ever built from
  exact renderings — the bright line of `cases/README.md` ("answer impossible to know") enforced
  as arithmetic.
- **Question-only probe (gate ≤ 0.60).** Bag-of-words Naive Bayes on question text alone must
  stay at chance: gold predictability from instructions+criteria is template/label leakage.
- **Keyword probe (gate: operator items ≤ 0.60).** A defect-cue heuristic must fail on
  operator-tagged items — difficulty earned by reasoning, not wording. (Easy items may be
  cue-solvable; that realism is deliberate.)
- **Round-trip re-answering (hook, currently skipped).** An external strong model re-answers the
  realized text; disagreement with the spine's gold is a *realization bug* (the text failed to
  express the spine) and the item is discarded. This automates the screening checklist.

Smoke run (`--n 3 --seed 1234`): 96 items, balance 0.50, question probe 0.521, keyword probe
0.510 overall / 0.521 operator items / 0.500 decoys; 56 unpinned rejects and 115 over-quota
refusals out of 267 draws.

## Worked example (real records from the smoke run)

Spine: `age_days <= 60 or defective`, gold computed by the interpreter.

| realization | state | gold | target P(yes) | arithmetic |
|---|---|---|---|---|
| explicit number, margin 5 over | "This request comes 65 days after the delivery. The service desk found nothing wrong with it." | no | **0.186** | .95 × margin(.86) = .81 |
| two dates, margin 5 over | "The delivery was on July 13 and today is September 16." | no | **0.314** | inferred-1 (.80) × margin(.86) = .69 |
| conflict + attribution, margin 45 over | "The customer says it arrived broken. Inspection found no faults." | no | **0.320** | inferred-1 (.80) × decisiveness(.85) = .68; the claim rides as rival evidence |

Same spine, provable gold, graded difficulty and graded probability — near-boundary items soften
toward 0.50 (margin 2 → 0.61 on an asserted measure), and evidence quality moves the target
independently of the gold.

## Splits, and the vessel experiment

Splits must be disjoint in **(spine seed x lexicon bank x domain)** — a held-out split that shares
templates with training measures dialect familiarity, not shape generalization. Two corpora, kept
separate:

- **shape** — spines with knowledge 0–1 (composition + decision form). This is the vessel's hull.
- **domain** — knowledge spines (injected background facts at levels 2–3) plus real domain rows.

The program's success metric is then the **sample-efficiency curve on post-training material**:
shape-trained vessel + N domain rows vs. base + N domain rows, scored on fresh-seeded external
samples (`just gen cfpb`, post-training seeds). Nothing in the generator may derive from the
locked benchmark suites: the spine inventory is authored from the rule algebra only, and every
record logs its seed and full parameter provenance. That is what makes a result *not* Von —
shape-fit without test exposure.

## Two surfaces per spine (the format ablation)

Every spine is realized twice from the same draws — prose (`state`) and semi-structured
(`state_kv`, e.g. `{"when": "early June; today is September 3", "condition": "Inspection found
no faults."}`). The kv surface keeps the semantic twists **in the values** (register inference,
attribution markers, conflict, decoy tokens) and gives away only fact framing: segmentation and
slot assignment. Keys are topic slots (`when`, `condition`, `condition_2`, `note`) and never
epistemic roles — "She says ..." in the value is what marks a claim (the epi-leak guard).
`--format prose|kv|both` selects the training surface (`both`, the default, keeps both fields
with shared gold and target for the paired-consistency arm). The ablation is the vessel
experiment's cheap axis: predicted kv ≈ prose on boundary/conflict/attribution tags, kv < prose
on coref/distractor, paired ≥ both — and if kv ≈ prose everywhere, the realizer is optional for
the hull and spine volume stops being gated by prose quality.

## Record schema (JSONL)

`id`, `family`, `domain`, `variant`, `primitive`, `question` (wire shape; `noul` rendered with
**neutral option keys** `a`/`b` and an `answer_map`, so fixed `false:`/`true:` label pairs cannot
become the shortcut), `state`, `state_kv` (unless `--format prose`), `expected`, `target` (soft
P(yes)), `annotations`, and `provenance` (generator version, seed, format, ops, rule string,
params, full statement trace).

## Roadmap

1. **More spine families, priority order**: conflict-weighted multi-option `choice`, `score`
   spines with rubric-anchored soft mixtures of adjacent levels, `Unless` exception shapes,
   negation-scope rule forms.
2. **Knowledge spines** (injected background facts, levels 2–3) for the domain corpus.
3. **LLM realization** alongside templates — same spine, many surfaces — gated by round-trip
   re-answering; question-side paraphrase banks (the question probe already guards the slot).
4. **Flip-test load-bearingness audit** for declared tags.
5. **Training integration**: soft-target proper scoring (log/spherical/RPS), then the shipped
   post-hoc input-conditioned calibration component — and the soft-vs-hard ablation.

## Risks

- **Realization bugs** (text does not express the spine): the round-trip gate plus sampled human
  audit; the interpreter's gold is only as good as the text-to-world correspondence.
- **Generator dialect becomes the new shortcut**: lexicon/template splits, LLM realization, and
  the standing external check on real fresh material.
- **Schedule arbitrariness**: the noisy-reader numbers are tunable; report calibration quality
  (ECE) per corpus and keep the hard-label baseline.
- **The 0.50 floor** discards gradient direction on very weak-evidence items (by design: the text
  genuinely underdetermines the answer there). If such items dominate a family, tighten the
  epistemic schedule instead of lowering the floor.
