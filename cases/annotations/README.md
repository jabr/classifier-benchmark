# Shape-vs-knowledge annotations

Sidecar annotations of every locked case in `v1.toml` and `v2.toml` (78 + 866 = 944), measuring two
independent properties of each case. These files are analysis data: they are not read by the
loader, the registry, or `just validate`, and the locked suites are untouched.

Purpose: separate the two things a case can demand — **semantic composition** (unwinding twists and
ambiguity between the state and the criteria) from **world knowledge** (facts neither the state nor
the criteria carry) — so recorded model errors in `results/` can be re-cut along those axes. That
tests whether small local models fail on problem *shape* (fixable with targeted training) or on
knowledge (fixable with domain data).

## Schema

`shape-knowledge.jsonl` — one JSON object per case, keyed by position in the locked suite file:

```json
{"case_id": "v2:secret_leak_v2:3", "twist": 2, "knowledge": 1, "tags": ["distractor", "paraphrase"],
 "crux": "composition", "unreachable": false, "note": "token named but explicitly absent"}
```

`case_id` is `<suite>:<task-id>:<0-based case index within the task>`, matching the order in the
TOML. Model run records in `results/` index cases the same way (for the three pre-lock † tasks
`grammar_issue`, `commit_intent`, `fair_housing_violation` the pre-lock index maps to the locked
index after skipping the case removed in `ec55df4` — see `bench/strata.py`).

### `twist` — semantic work between state and gold (0–3)

Ignores what the reader knows; measures only how much inference the *text* demands.

| Value | Meaning |
|---|---|
| 0 | **Direct.** The state states the qualifying fact in essentially the criteria's terms. Wording-level match, no inference. |
| 1 | **Bridge.** One inference step: synonym/hypernym paraphrase, light coreference, a plain rephrasing of the criterion into the state's register. |
| 2 | **Operator.** One non-trivial semantic operator fixes or flips the answer: negation or stated absence, an exception ("unless…"), boundary arithmetic (dates, counts, thresholds), a distractor near-miss, attribution ("the reporter *claims* it's fine"), a hypothetical mention. |
| 3 | **Interaction.** Two or more operators interact (negation scope over an exception, boundary inside a conditional), or evidence conflicts and must be weighed (two spans pushing different answers, resolved by scope or strength). |

### `knowledge` — background knowledge beyond the state and criteria (0–3)

Ask: *remove the reader's background knowledge down to level X — can they still reach the gold?*

| Value | Meaning |
|---|---|
| 0 | **None.** A fluent reader of the language reaches the gold from state + criteria alone. |
| 1 | **Everyday.** Common practical or cultural knowledge (what "double-charged" implies; that a reset email should arrive). |
| 2 | **Professional.** Standard literacy of a practitioner in the domain: SQL syntax, recognizable credential formats, clinical symptom patterns, ingredient literacy, programming fluency. |
| 3 | **Specialist.** Knowledge a careful generalist would plausibly lack: niche regulations, statute specifics, obscure hazard classes, vendor-specific trivia. |

### `tags` — which twist operators are load-bearing (list, may be empty)

`negation`, `exception`, `boundary`, `distractor`, `attribution`, `coref`, `conflict`, `paraphrase`,
`implicit`. `paraphrase` means a *non-obvious* lexical gap must be bridged (ordinary synonymy is
just `twist: 1`); `implicit` means the qualifying fact is implied, never stated; `coref` means
tracking references across clauses/sentences is required; `conflict` means candidate evidence spans
push different answers.

### `crux` — the component that decides the label (single value)

- `direct` — little work anywhere; recognition suffices.
- `composition` — twist resolution decides the answer.
- `knowledge` — the background-fact gap decides it.
- `decision` — comprehension is easy but the *decision rule* is the hard part: placing a level on an
  ordinal scale, choosing between near-equal options, a threshold judgment call.

### `unreachable` — the screening bright line (bool)

`true` if the gold is **not** reachable from state + criteria + level ≤2 knowledge — a missing fact,
or a gold that contradicts the question's own definitions (the `cases/ISSUES.md` v1
`incident_severity` cases are the reference type). Should be rare; its presence is a finding, not
noise.

## Calibration examples (invented, not from the suites)

1. noul "Does this message contain a shipping address?" — state: *"Sure, ship it to 12 Elm St."*
   → `twist: 1`, `knowledge: 0`, `tags: ["implicit", "paraphrase"]`, `crux: "composition"`. The
   phrase "ship it to" never says "address"; that's a one-step bridge, no outside facts.
2. noul "Is the return inside the 30-day window?" — state: *"Purchased March 2, today is March 31."*
   → `twist: 2`, `knowledge: 1`, `tags: ["boundary"]`, `crux: "composition"`. Boundary arithmetic is
   the load-bearing operator; knowing March has 31 days is everyday knowledge.
3. choice with a decoy — criteria: `billing` = invoices and charges, `tech` = bugs and failures;
   state: *"The invoice PDF is corrupted and won't open at all."*
   → `twist: 2`, `knowledge: 1`, `tags: ["distractor"]`, `crux: "composition"`. "Invoice" is a
   lexical decoy; the failure mode makes it `tech`.
4. score on a 3-level severity scale — state: *"One customer's export job slowed down for ten
   minutes and recovered on its own."*
   → `twist: 1`, `knowledge: 1`, `tags: []`, `crux: "decision"`. Comprehension is trivial; placing
   the level against the rubric is the whole question.

## Provenance and method

- Annotated by LLM annotators (MiMo V2.6 Pro sub-agents), **blind to `results/`** — no annotator saw
  any model's predictions, so twist/knowledge scores cannot be biased toward known errors.
- Six annotators, each covering a disjoint set of tasks plus the same shared 24-case reliability
  set (stratified by type and suite); pairwise agreement on the shared set is reported in
  `results/shape-knowledge.md`.
- Gold labels were visible to annotators (the question is how hard the path *to* the gold is).
- `shape-knowledge.jsonl` carries the owning annotator's record per case; every shared-set vote
  from all six annotators is preserved verbatim in `agreement.json`.

## Caveats

- Same-model double annotation measures context noise, not model-family bias: an LLM's sense of
  "specialist knowledge" differs from a human expert's. Treat level boundaries (1↔2 especially) as
  fuzzy; the analysis bins to low/high halves for that reason.
- Annotations describe cases, not tasks: a task's cases deliberately span the twist scale.