"""Logical spines: labeled logical forms whose gold answer is known by construction.

A spine is a (world, rule, question) triple over the System One wire shape. The
interpreter evaluates the rule over the world and returns the gold answer, the
evidence trace, and the noisy-reader soft target — so gold labels are defensible
by construction and `cases/README.md`'s screening line becomes a property of the
generator, not a review step.

The noisy-reader schedule (strength by epistemic status, conflict decisiveness,
boundary margin softening) is a set of hyperparameters, not a law: it defines
the soft targets that teach the probability axis (see results/shape-knowledge.md,
"Decision form"), and it should be ablated against hard labels per corpus.
"""

from dataclasses import dataclass, field
from enum import Enum


class Epi(str, Enum):
  """How the text establishes a fact — drives evidence strength."""

  VERIFIED = "verified"        # established by an authoritative source (inspection, system log)
  ASSERTED = "asserted"        # stated flatly
  PARAPHRASED = "paraphrased"  # stated in non-obvious wording (one bridge step)
  INFERRED = "inferred"        # implied only; `depth` inference steps away
  CLAIMED = "claimed"          # attributed claim; not established (claim != fact)


# Noisy-reader strengths: P(a careful reader reaches the fact from the text).
STRENGTH = {Epi.VERIFIED: 0.97, Epi.ASSERTED: 0.95, Epi.PARAPHRASED: 0.90, Epi.CLAIMED: 0.60}
INFERRED_STRENGTH = 0.80  # minus 0.10 per extra inference step, floored at 0.50

# Conflict-resolution decisiveness: explicit priority rules read clearer than heuristics.
POLICY_DECISIVENESS = {"verified": 0.85, "ranked": 0.85, "recent": 0.70}

TARGET_CAP = 0.97  # targets never touch 0/1 — the reader is never perfect


def strength_of(statement: "Statement") -> float:
  if statement.epi is Epi.INFERRED:
    return max(0.50, INFERRED_STRENGTH - 0.10 * max(0, statement.depth - 1))
  return STRENGTH[statement.epi]


@dataclass(frozen=True)
class Statement:
  key: str
  value: object            # bool property, numeric measure (derived measures allowed)
  epi: Epi = Epi.ASSERTED
  speaker: str | None = None
  depth: int = 0           # inference-chain depth for Epi.INFERRED
  note: str = ""           # provenance for the evidence trace


@dataclass(frozen=True)
class Resolution:
  value: object
  winner: Statement | None
  rivals: tuple["Statement", ...]
  decisiveness: float      # 1.0 = unanimous; conflicts discount the target


@dataclass
class World:
  statements: list[Statement]
  policy: dict[str, str] = field(default_factory=dict)      # key -> conflict policy
  authority: dict[str, int] = field(default_factory=dict)   # speaker -> rank (1 wins)

  def resolve(self, key: str) -> Resolution:
    """The settled value for a key. Multiple statements on one key are legal only
    with an explicit resolution policy — conflicts must never be implicit."""
    mine = [s for s in self.statements if s.key == key]
    if not mine:
      raise KeyError(key)
    if len(mine) == 1:
      return Resolution(mine[0].value, mine[0], (), 1.0)
    policy = self.policy.get(key)
    if policy is None:
      raise ValueError(f"{key!r} has {len(mine)} statements but no conflict policy")
    if policy == "verified":
      verified = [s for s in mine if s.epi is Epi.VERIFIED]
      if not verified:
        raise ValueError(f"{key!r}: policy 'verified' needs a VERIFIED statement")
      winner = verified[0]
    elif policy == "ranked":
      winner = min(mine, key=lambda s: self.authority.get(s.speaker or "", 99))
    elif policy == "recent":
      winner = mine[-1]
    else:
      raise ValueError(f"{key!r}: unknown conflict policy {policy!r}")
    return Resolution(
      winner.value,
      winner,
      tuple(s for s in mine if s is not winner),
      POLICY_DECISIVENESS[policy],
    )


@dataclass(frozen=True)
class Verdict:
  gold: bool
  support: tuple[Statement, ...]    # evidence establishing the gold
  rivals: tuple[Statement, ...]     # conflicting evidence (resolution losers, bare claims)
  decisiveness: float
  margin: float | None              # |value - threshold| of the tightest boundary call
  near: float | None                # that boundary's near-scale


@dataclass(frozen=True)
class Judgment:
  gold: bool
  p_yes: float                      # noisy-reader soft target for the yes branch
  strength: float                   # effective evidence strength for the gold
  decisiveness: float
  margin: float | None
  near: float | None
  support: tuple[Statement, ...]
  rivals: tuple[Statement, ...]


def _combine(parts: list[Verdict], gold: bool) -> Verdict:
  """Merge branch verdicts: the branches agreeing with `gold` establish it.
  Off-gold branch evidence settles nothing about the combined answer and is
  dropped (its route was not taken), and so are its rivals — a claim that would
  not flip the combined gold is redundant, not conflicting."""
  matching = [p for p in parts if p.gold == gold]
  support = tuple(s for p in matching for s in p.support)
  rivals = tuple(s for p in matching for s in p.rivals)
  decisiveness = min((p.decisiveness for p in matching), default=1.0)
  ratios = [(p.margin / p.near, p.margin, p.near) for p in matching
            if p.margin is not None and p.near]
  if ratios:
    _, margin, near = min(ratios)
  else:
    margin = near = None
  return Verdict(gold, support, rivals, decisiveness, margin, near)


class Rule:
  def eval(self, world: World) -> Verdict:
    raise NotImplementedError


@dataclass(frozen=True)
class Compare(Rule):
  """Boundary arithmetic: a measure against a threshold (dates, counts, amounts)."""

  key: str
  op: str                  # one of "<", "<=", ">", ">="
  threshold: float
  near: float = 7.0        # |margin| below this is a near-boundary judgment call

  def eval(self, world: World) -> Verdict:
    r = world.resolve(self.key)
    value = r.value
    checks = {"<": value < self.threshold, "<=": value <= self.threshold,
              ">": value > self.threshold, ">=": value >= self.threshold}
    if self.op not in checks:
      raise ValueError(f"unknown comparison op {self.op!r}")
    return Verdict(checks[self.op], (r.winner,), r.rivals, r.decisiveness,
                   abs(value - self.threshold), self.near)


@dataclass(frozen=True)
class Holds(Rule):
  """A property holds. Attribution contract: an attributed claim (CLAIMED) does
  not establish the property — it counts as rival evidence instead."""

  key: str
  want: bool = True

  def eval(self, world: World) -> Verdict:
    try:
      r = world.resolve(self.key)
    except KeyError:
      return Verdict(self.want is False, (), (), 1.0, None, None)
    claimed = r.winner.epi is Epi.CLAIMED
    established = bool(r.value) and not claimed
    gold = established == self.want
    if claimed:
      return Verdict(gold, (), (r.winner,) + r.rivals, r.decisiveness * 0.70, None, None)
    return Verdict(gold, (r.winner,), r.rivals, r.decisiveness, None, None)


@dataclass(frozen=True)
class Not(Rule):
  rule: Rule

  def eval(self, world: World) -> Verdict:
    v = self.rule.eval(world)
    return _combine([Verdict(not v.gold, v.support, v.rivals, v.decisiveness,
                             v.margin, v.near)], not v.gold)


@dataclass(frozen=True)
class And(Rule):
  rules: tuple[Rule, ...]

  def eval(self, world: World) -> Verdict:
    parts = [r.eval(world) for r in self.rules]
    return _combine(parts, all(p.gold for p in parts))


@dataclass(frozen=True)
class Or(Rule):
  rules: tuple[Rule, ...]

  def eval(self, world: World) -> Verdict:
    parts = [r.eval(world) for r in self.rules]
    return _combine(parts, any(p.gold for p in parts))


@dataclass(frozen=True)
class Unless(Rule):
  """'...unless <exception>': the exception clause selects the case class."""

  base: Rule
  exception: Rule

  def eval(self, world: World) -> Verdict:
    b = self.base.eval(world)
    e = self.exception.eval(world)
    flipped = Verdict(not e.gold, e.support, e.rivals, e.decisiveness, e.margin, e.near)
    return _combine([b, flipped], b.gold and flipped.gold)


def interpret(world: World, rule: Rule) -> Judgment:
  """Gold + noisy-reader soft target P(yes).

  strength = weakest-link evidence x conflict decisiveness x boundary margin,
  floored at 0.5 so the soft target never contradicts the gold.
  """
  v = rule.eval(world)
  base = min((strength_of(s) for s in v.support), default=0.50)
  boundary = 1.0 if v.margin is None or not v.near else 0.5 + 0.5 * min(1.0, v.margin / v.near)
  strength = min(TARGET_CAP, max(0.50, base * v.decisiveness * boundary))
  p_yes = strength if v.gold else 1.0 - strength
  return Judgment(v.gold, p_yes, strength, v.decisiveness, v.margin, v.near,
                  v.support, v.rivals)
