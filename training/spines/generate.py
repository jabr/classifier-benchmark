"""Boundary-family generator, end to end: spine -> realization -> checks -> JSONL.

The first spine family from training/spines/README.md: threshold eligibility
(`age_days <= T or defective`) realized across domain slots, renderings, and
semantic variations. Every record carries its gold (computed by the
interpreter), the noisy-reader soft target, the free rubric annotations, and
full provenance (seed, params, statements) so any item can be rebuilt.

Gold-defensibility is enforced mechanically: a rendering's reader-side imprecision
(RENDERINGS[..] fudge, plus display rounding error) must fit strictly inside the
item's margin to the threshold, or the item is never emitted.

Each spine is realized on two surfaces from the same draws: prose (`state`) and
semi-structured (`state_kv` — topic-slot keys, verbatim cue values) for the
kv-vs-prose format ablation. Keys name topics only, never epistemic roles: the
claim/refutation register stays in the values, where the model must read it.

Usage:
  uv run python -m training.spines.generate --n 4 --seed 1234 --out spines.jsonl
  uv run python -m training.spines.generate --format kv --out spines-kv.jsonl
  uv run python -m training.spines.generate --self-test
"""

import argparse
import json
import random
import re
import sys
from dataclasses import dataclass
from datetime import date, timedelta

from training.spines.realize import RENDERINGS, annotate
from training.spines.spine import (
  Epi,
  Holds,
  Or,
  Compare,
  Statement,
  World,
  interpret,
)

GENERATOR = "training.spines.generate"
VERSION = 2  # v2: dual-surface records (state + state_kv)
MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]
NUMBER_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
                7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven",
                12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen"}
MARGINS = [2, 5, 9, 25, 45]           # days of age distance from the threshold
KEYWORDS_YES = {"defect", "defective", "damaged", "broken", "faulty", "cracked", "dead", "dmg"}


@dataclass(frozen=True)
class Domain:
  name: str
  threshold: int
  event: str            # what starts the clock
  event_verb: str       # past tense for relative phrasing
  subject: str          # the claimant
  pronoun: str          # the claimant's pronoun for coref chains
  thing: str            # the claimed object (no article)
  question_forms: tuple[str, ...]
  yes_desc: str
  no_desc: str
  true_lines: tuple[str, ...]
  paraphrase_true_lines: tuple[str, ...]
  refuted_lines: tuple[str, ...]
  absence_lines: tuple[str, ...]
  denial_lines: tuple[str, ...]
  claim_lines: tuple[str, ...]
  decoy_lines: tuple[str, ...]


DOMAINS = [
  Domain(
    name="retail_return", threshold=60, event="delivery", event_verb="delivered",
    subject="the customer", pronoun="she", thing="item",
    question_forms=(
      "Is this request eligible for a refund under the return policy?",
      "Does this refund request qualify under the stated return policy?",
      "Under the return policy as written, should this request be approved?",
    ),
    yes_desc="the request qualifies under the policy",
    no_desc="the request does not qualify",
    true_lines=("The {thing} arrived damaged.", "It was dead on arrival."),
    paraphrase_true_lines=("It never worked — completely DOA.", "Nothing ever powered it on."),
    refuted_lines=("Inspection found no faults.", "The service desk found nothing wrong with it."),
    absence_lines=("There is no record of any defect.", "Nothing in the file indicates damage."),
    denial_lines=("She insists it was not damaged.", "{Subject} denies anything was broken."),
    claim_lines=("{Subject} says it arrived broken.", "According to {subject}, the {thing} was faulty."),
    decoy_lines=("The confirmation email mentions our 90-day price guarantee and a broken promo code.",),
  ),
  Domain(
    name="warranty_claim", threshold=365, event="purchase", event_verb="bought",
    subject="the claimant", pronoun="he", thing="unit",
    question_forms=(
      "Is this claim still covered under the warranty terms?",
      "Does this warranty claim fall inside the coverage period as stated?",
      "Under the warranty terms as written, is this claim covered?",
    ),
    yes_desc="the claim is inside the coverage period or covered by the defect clause",
    no_desc="the claim falls outside the coverage terms",
    true_lines=("The {thing} failed with a manufacturing defect.", "It stopped working on its own."),
    paraphrase_true_lines=("It bricked itself within the year.", "The mainboard gave out for no reason."),
    refuted_lines=("The inspection found user damage, not a defect.", "Teardown shows no manufacturing fault."),
    absence_lines=("There is no record of any defect.", "Nothing in the claim indicates a fault."),
    denial_lines=("He insists it was never dropped.", "{Subject} denies any mishandling."),
    claim_lines=("{Subject} says the {thing} simply died.", "According to {subject}, it failed on its own."),
    decoy_lines=("The claim references our 90-day express replacement plan and a broken seal photo.",),
  ),
]


@dataclass(frozen=True)
class Variant:
  name: str
  ops: tuple[str, ...]
  rendering: str
  props: tuple[str, ...]


VARIANTS = [
  Variant("explicit", ("boundary",), "number", ("silent", "true", "refuted")),
  Variant("dates", ("boundary",), "dates", ("silent", "true", "refuted")),
  Variant("relative", ("boundary", "paraphrase"), "relative", ("silent", "true", "refuted")),
  Variant("implicit-coref", ("boundary", "implicit", "coref"), "vague", ("silent", "true", "refuted")),
  Variant("negation", ("boundary", "negation"), "dates", ("absence", "denial")),
  Variant("attribution", ("boundary", "attribution"), "dates", ("claim",)),
  Variant("conflict", ("boundary", "attribution", "conflict"), "dates", ("conflict",)),
  Variant("decoy", ("boundary", "distractor"), "dates", ("silent", "true", "refuted")),
]


def fmt_day(d: date, with_year: bool = False) -> str:
  year = f", {d.year}" if with_year else ""
  return f"{MONTHS[d.month - 1]} {d.day}{year}"


def month_part(d: date, with_year: bool = False) -> str:
  part = "early" if d.day <= 10 else "mid" if d.day <= 20 else "late"
  year = f" {d.year}" if with_year else ""
  return f"{part} {MONTHS[d.month - 1]}{year}"


def age_render(rng: random.Random, dom: Domain, rendering: str, age: int,
               today: date, coref: bool) -> tuple[str, str]:
  """(prose sentence, kv cue phrase) from one draw, so both surfaces carry
  exactly the same cues — only the frame differs."""
  src = today - timedelta(days=age)
  # A dropped year would make the age uncomputable: dates carry the year whenever
  # the span crosses one (the warranty domain's always does).
  crossed = src.year != today.year
  if rendering == "number":
    forms = ((f"It has been {age} days since the {dom.event}.",
              f"{age} days after the {dom.event}"),
             (f"This request comes {age} days after the {dom.event}.",
              f"{age} days after the {dom.event}"))
    return rng.choice(forms)
  if rendering == "dates":
    cue = f"{fmt_day(src, crossed)}; today is {fmt_day(today, crossed)}"
    return (f"The {dom.event} was on {fmt_day(src, crossed)} and today is "
            f"{fmt_day(today, crossed)}.", cue)
  if rendering == "relative":
    if age <= 120:
      amount, unit = round(age / 7), "week"
    else:
      amount, unit = round(age / 30), "month"
    word = NUMBER_WORDS.get(amount, str(amount))
    plural = unit if amount == 1 else unit + "s"
    return (f"The {dom.thing} was {dom.event_verb} about {word} {plural} ago.",
            f"about {word} {plural} ago")
  cue = f"{month_part(src, crossed)}; today is {fmt_day(today, crossed)}"
  if coref:
    return (f"It came through in {month_part(src, crossed)}. "
            f"{dom.pronoun.capitalize()} is only raising it now, on {fmt_day(today, crossed)}.",
            cue)
  return (f"The {dom.event} was in {month_part(src, crossed)}, and today is "
          f"{fmt_day(today, crossed)}.", cue)


def prop_lines(rng: random.Random, dom: Domain, variant: Variant, prop: str) -> list[str]:
  fmt = lambda s: s.format(thing=dom.thing, subject=dom.subject,
                           Subject=dom.subject.capitalize())
  if prop == "silent":
    return []
  if prop == "true":
    bank = dom.paraphrase_true_lines if "paraphrase" in variant.ops else dom.true_lines
    return [fmt(rng.choice(bank))]
  if prop == "absence":
    return [fmt(rng.choice(dom.absence_lines))]
  if prop == "denial":
    return [fmt(rng.choice(dom.denial_lines))]
  if prop == "claim":
    return [fmt(rng.choice(dom.claim_lines))]
  if prop == "refuted":
    return [fmt(rng.choice(dom.refuted_lines))]
  if prop == "conflict":
    return [fmt(rng.choice(dom.claim_lines)), fmt(rng.choice(dom.refuted_lines))]
  raise ValueError(prop)


def prop_statements(prop: str, subject: str) -> tuple[list[Statement], dict[str, str]]:
  """The world behind the property line (epistemic status is the operator's contract)."""
  claim = Statement("defective", True, Epi.CLAIMED, speaker=subject, note="attributed claim")
  if prop == "silent":
    return [], {}
  if prop == "true":
    return [Statement("defective", True, Epi.ASSERTED, note="asserted defect")], {}
  if prop == "claim":
    return [claim], {}
  if prop in ("absence", "denial"):
    return [Statement("defective", False, Epi.ASSERTED, note="stated absence / negation")], {}
  if prop == "refuted":
    return [Statement("defective", False, Epi.VERIFIED, speaker="inspection", note="inspection")], {}
  if prop == "conflict":
    return ([claim, Statement("defective", False, Epi.VERIFIED, speaker="inspection",
                              note="inspection contradicts the claim")],
            {"defective": "verified"})
  raise ValueError(prop)


def age_statement(rendering: str, age: int) -> Statement:
  epi_name, depth, _, _, _ = RENDERINGS[rendering]
  epi = Epi.INFERRED if epi_name == "inferred" else Epi(epi_name)
  note = {"number": "age stated directly", "dates": "age computed from two dates",
          "relative": "age converted from a fuzzy week count",
          "vague": "age read off a month register"}[rendering]
  return Statement("age_days", age, epi, depth=depth, note=note)


def display_error(rendering: str, age: int) -> int:
  """Reader-side imprecision introduced by how the number is displayed."""
  if rendering == "relative":
    if age <= 120:
      return abs(7 * round(age / 7) - age) + 3   # "about N weeks" phrasing slack
    return abs(30 * round(age / 30) - age) + 8   # "about N months" phrasing slack
  return 0


def self_test() -> None:
  from training.spines.realize import crux_for, twist_for
  # Calibration expectations from cases/annotations/README.md (invented examples):
  assert twist_for({"implicit", "paraphrase"}, False) == 1   # ex 1: bridge work only
  assert twist_for({"boundary"}, True) == 2                  # ex 2: date arithmetic
  assert twist_for({"distractor"}, False) == 2               # ex 3: near-miss decoy
  assert twist_for({"boundary"}, False) == 1                 # stated-number compare
  assert twist_for({"conflict", "attribution"}, True) == 3   # evidence must be weighed
  assert crux_for(1, 2, 7.0) == "decision"                   # ex 4 shape: threshold call
  assert crux_for(2, 2, 7.0) == "composition"
  assert crux_for(1, 25, 7.0) == "direct"
  print("self-test ok", file=sys.stderr)


def build_item(rng: random.Random, dom: Domain, variant: Variant, seq: int,
               today: date, want_gold: bool) -> tuple[dict | None, str]:
  """One candidate: (item, "") on success, else (None, reason) — 'unpinned' when
  the text cannot defend the gold this close to the cut, 'wrong-label' when that
  label's quota is already filled."""
  side = rng.choice([-1, 1])
  margin = rng.choice(MARGINS)
  age = dom.threshold + side * margin
  prop = rng.choice(variant.props)
  fudge = RENDERINGS[variant.rendering][4]
  if margin <= fudge + display_error(variant.rendering, age):
    return None, "unpinned"

  statements = [age_statement(variant.rendering, age)]
  prop_stmts, policy = prop_statements(prop, dom.subject)
  statements += prop_stmts
  world = World(statements, policy=policy, authority={dom.subject: 2, "inspection": 1})
  rule = Or((Compare("age_days", "<=", dom.threshold, near=7.0), Holds("defective")))
  j = interpret(world, rule)
  if j.gold != want_gold:
    return None, "wrong-label"  # quota sampling: only take labels we still need

  coref = "coref" in variant.ops
  age_sentence, age_cue = age_render(rng, dom, variant.rendering, age, today, coref)
  props = prop_lines(rng, dom, variant, prop)   # verbatim phrases double as kv cues
  decoy = rng.choice(dom.decoy_lines) if "distractor" in variant.ops else None
  parts = [age_sentence] + props
  if decoy:
    parts.append(decoy)
  state = " ".join(parts)
  # The kv surface: topic-slot keys, verbatim cue values. Keys stay
  # epistemics-free — "She says ..." is what marks a claim, and that lives in
  # the value (the epi-leak guard).
  slots = {"when": age_cue}
  for i, phrase in enumerate(props):
    slots["condition" if i == 0 else "condition_2"] = phrase
  if decoy:
    slots["note"] = decoy
  state_kv = json.dumps(slots, ensure_ascii=False)
  instructions = rng.choice(dom.question_forms)
  annotations = annotate(set(variant.ops), variant.rendering, j.margin, j.near)
  item = {
    "id": f"boundary:{dom.name}:{variant.name}:{seq:04d}",
    "family": "boundary",
    "domain": dom.name,
    "variant": variant.name,
    "primitive": "noul",
    "question": {"type": "noul", "instructions": instructions,
                 "criteria": {"a": dom.yes_desc, "b": dom.no_desc}},
    "state": state,
    "state_kv": state_kv,
    "expected": j.gold,
    "target": round(j.p_yes, 4),
    "answer_map": {"a": True, "b": False},
    "annotations": annotations,
    "provenance": {
      "generator": GENERATOR,
      "version": VERSION,
      "seed": None,  # stamped by generate() with the run seed
      "ops": list(variant.ops),
      "rendering": variant.rendering,
      "rule": f"age_days <= {dom.threshold} or defective",
      "params": {"threshold": dom.threshold, "age_days": age, "margin": margin,
                 "side": side, "prop": prop, "today": today.isoformat()},
      "statements": [{"key": s.key, "value": s.value, "epi": s.epi.value,
                      "speaker": s.speaker, "depth": s.depth, "note": s.note}
                     for s in statements],
    },
  }
  return item, ""


def generate(seed: int, n: int, domains: list[Domain], variants: list[Variant],
             fmt: str = "both"):
  """n items per (domain x variant x label) cell, balanced by construction.
  fmt selects the training surface: 'prose' (state only), 'kv' (state = the kv
  string), or 'both' (paired arm: state + state_kv, shared gold and target)."""
  rng = random.Random(seed)
  items, rejects = [], {"unpinned": 0, "wrong-label": 0}
  for dom in domains:
    for variant in variants:
      quotas = {True: n, False: n}
      seq = 0
      attempts = 0
      while sum(quotas.values()) > 0 and attempts < 40 * n:
        attempts += 1
        want = True if quotas[True] > 0 and (quotas[False] == 0 or rng.random() < 0.5) else False
        today = date(2026, 9, 1) + timedelta(days=rng.randrange(30))
        item, reason = build_item(rng, dom, variant, seq, today, want)
        if item is None:
          rejects[reason] += 1
          continue
        item["provenance"]["seed"] = seed
        item["provenance"]["format"] = fmt
        if fmt == "prose":
          del item["state_kv"]
        elif fmt == "kv":
          item["state"] = item.pop("state_kv")
        quotas[want] -= 1
        items.append(item)
        seq += 1
      if sum(quotas.values()) > 0:
        print(f"warn: unfilled quota {dom.name}/{variant.name}: {quotas}", file=sys.stderr)
  return items, rejects


def _tokens(text: str) -> list[str]:
  return re.findall(r"[a-z0-9']+", text.lower())


def question_probe(items: list[dict]) -> float:
  """Bag-of-words Naive Bayes on question text alone. Anything above chance here
  is template/label leakage (anti-shortcut gate #1)."""
  def text_of(it):
    q = it["question"]
    return q["instructions"] + " " + " ".join(q["criteria"].values())

  order = list(range(len(items)))
  random.Random(0).shuffle(order)
  train, test = order[: len(order) // 2], order[len(order) // 2:]
  counts = {True: {}, False: {}}
  totals = {True: 0, False: 0}
  for i in train:
    lab = items[i]["expected"]
    for tok in _tokens(text_of(items[i])):
      counts[lab][tok] = counts[lab].get(tok, 0) + 1
      totals[lab] += 1
  vocab = len({t for lab in counts for t in counts[lab]})
  hits = 0
  for i in test:
    scores = {}
    for lab in (True, False):
      s = 0.0
      for tok in _tokens(text_of(items[i])):
        s += ((counts[lab].get(tok, 0) + 1) / (totals[lab] + vocab))
      scores[lab] = s
    hits += (scores[True] >= scores[False]) == items[i]["expected"]
  return hits / max(1, len(test))


def keyword_probe(items: list[dict], field: str = "state") -> tuple[float, float, float]:
  """Keyword heuristic (predict yes iff a defect cue appears). Gate: it must fail
  on the operator items — difficulty has to be earned by reasoning
  (cases/README.md), so lexical cues cannot decide those. Returns (overall, on
  operator-tagged items, on distractor-tagged items) for the given surface."""
  def predict(it):
    return bool(KEYWORDS_YES & set(_tokens(it[field])))

  def acc(sub):
    return sum(predict(it) == it["expected"] for it in sub) / max(1, len(sub))

  ops_tagged = [it for it in items
                if set(it["annotations"]["tags"]) & {"distractor", "negation", "conflict", "attribution"}]
  decoys = [it for it in items if "distractor" in it["annotations"]["tags"]]
  return acc(items), acc(ops_tagged), acc(decoys)


def report(items: list[dict], rejects: dict[str, int]) -> bool:
  ok = True
  n = len(items)
  yes = sum(1 for it in items if it["expected"])
  print(f"items: {n}  (rejected: {rejects['unpinned']} unpinned, "
        f"{rejects['wrong-label']} over-quota label)", file=sys.stderr)
  print(f"balance: yes={yes} ({yes / n:.2f})  no={n - yes}", file=sys.stderr)
  if not 0.4 <= yes / n <= 0.6:
    print("gate FAIL: label balance outside [0.40, 0.60]", file=sys.stderr)
    ok = False
  qp = question_probe(items)
  print(f"question-only probe: {qp:.3f}  (gate: <= 0.60)", file=sys.stderr)
  if qp > 0.60:
    print("gate FAIL: question text leaks the label", file=sys.stderr)
    ok = False
  surfaces = ["state"] + (["state_kv"] if "state_kv" in items[0] else [])
  for field in surfaces:
    kw, kw_ops, kw_decoy = keyword_probe(items, field)
    print(f"keyword probe [{field}]: overall {kw:.3f}, operator items {kw_ops:.3f}, "
          f"decoys {kw_decoy:.3f}  (gate: operator items <= 0.60)", file=sys.stderr)
    if kw_ops > 0.60:
      print(f"gate FAIL: lexical cues decide the operator items ({field})", file=sys.stderr)
      ok = False
  print("round-trip re-answering: skipped (requires an external re-answerer)", file=sys.stderr)
  return ok


def main() -> None:
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("--n", type=int, default=3, help="items per (domain x variant x label) quota")
  ap.add_argument("--seed", type=int, default=1234)
  ap.add_argument("--out", default="-", help="JSONL output path, or - for stdout")
  ap.add_argument("--format", choices=("prose", "kv", "both"), default="both",
                  help="training surface: prose state, kv state, or both (paired arm)")
  ap.add_argument("--self-test", action="store_true", help="check the rubric mapping expectations")
  args = ap.parse_args()
  if args.self_test:
    self_test()
    return
  items, rejects = generate(args.seed, args.n, DOMAINS, VARIANTS, args.format)
  out = sys.stdout if args.out == "-" else open(args.out, "w")
  for it in items:
    out.write(json.dumps(it) + "\n")
  if out is not sys.stdout:
    out.close()
  ok = report(items, rejects)
  sys.exit(0 if ok else 1)


if __name__ == "__main__":
  main()
