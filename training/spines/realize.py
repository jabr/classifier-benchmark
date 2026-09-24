"""Semantic variation layer: the operator catalog with label contracts, and the
mapping from operator traces to the rubric's annotations.

Operators carry two things: a contract (what the operator promises about the
gold — the reason generated labels stay defensible through variation) and a
weight used to compute the free twist/knowledge annotations that match the
hand-annotation rubric in cases/annotations/README.md. The mapping below is an
operationalization of that rubric; the rubric remains authoritative, and its
four calibration examples are checked against `twist_for` in the generator's
self-test expectations.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Op:
  name: str        # tag vocabulary of cases/annotations/README.md
  weight: str      # "heavy" | "bridge" | "conflict"
  contract: str    # what the operator promises about the label


OPS: dict[str, Op] = {
  name: Op(name, weight, contract)
  for name, weight, contract in [
    ("paraphrase", "bridge", "gold preserved; a non-obvious wording gap must be bridged"),
    ("coref", "bridge", "gold preserved; references must be tracked across clauses"),
    ("implicit", "bridge", "gold via an inference chain (depth counted in epi)"),
    ("boundary", "heavy", "gold via date/count/threshold arithmetic; margin parameterized"),
    ("negation", "heavy", "gold gates on stated absence or negation scope"),
    ("exception", "heavy", "an 'unless' clause selects the case class"),
    ("distractor", "heavy", "gold preserved; a near-miss or keyword decoy is present"),
    ("attribution", "heavy", "claim != fact; an attributed claim is not establishment"),
    ("conflict", "conflict", "two sources disagree; the spine's resolution policy decides"),
  ]
}

# Rendering demand of a measure (how the text states the number the rule needs).
RENDERINGS = {
  # name: (epi, depth, arithmetic demanded, knowledge level, reader fudge in days)
  "number": ("asserted", 0, False, 0, 0),     # "65 days after purchase" — plain comparison
  "dates": ("inferred", 1, True, 1, 0),       # two calendar dates — exact arithmetic
  "relative": ("inferred", 1, True, 1, 5),    # "about six weeks ago" — unit arithmetic, fuzzy
  "vague": ("inferred", 2, True, 1, 14),      # "mid-summer" — imprecise register
}


def twist_for(ops: set[str], boundary_arithmetic: bool) -> int:
  """Rubric twist scale: 3 = interacting operators or conflicting evidence,
  2 = one non-trivial operator, 1 = bridge work only, 0 = direct."""
  if "conflict" in ops:
    return 3
  heavy = sum(1 for name in ops if OPS[name].weight == "heavy")
  if "boundary" in ops and not boundary_arithmetic:
    heavy -= 1  # a stated-number threshold call is a plain comparison, not arithmetic
  if heavy >= 2:
    return 3
  if heavy == 1:
    return 2
  return 1 if ops else 0


def knowledge_for(rendering: str) -> int:
  """Knowledge demand of the rendering (calendar/unit literacy counts as everyday)."""
  return RENDERINGS[rendering][3]


def crux_for(twist: int, margin: float | None, near: float | None) -> str:
  if twist >= 2:
    return "composition"
  if margin is not None and near is not None and margin < near:
    return "decision"    # comprehension trivial; the threshold call is the hard part
  return "direct"


def annotate(ops: set[str], rendering: str, margin: float | None, near: float | None) -> dict:
  """The free annotations: twist/knowledge/tags/crux in the sidecar schema
  (cases/annotations/README.md), computed from the operator trace."""
  _, _, arithmetic, _, _ = RENDERINGS[rendering]
  twist = twist_for(ops, arithmetic)
  return {
    "twist": twist,
    "knowledge": knowledge_for(rendering),
    "tags": sorted(ops),
    "crux": crux_for(twist, margin, near),
    "unreachable": False,
  }
