"""Vendored core of logan-markewich/jeff (MIT) — prompt folding and score decoding.

Adapted from src/jeff/core/groups.py and src/jeff/core/answers.py at
https://github.com/logan-markewich/jeff (main, Sep 2026), reduced to the
single-question in-process path and the server-default PromptOptions
(instruction_as_name, fold_descriptions, yes_no nouls; T=3.2). The bench
harness issues exactly one question per request, which reproduces jeff's
default `isolate: nouls` behavior: choice/score and each noul each get their
own encoder pass. Keeps probabilities/comparable to the server rows.
"""

from dataclasses import dataclass

from bench.cases import Choice, Noul, Score

EPS = 1e-9
# Fit by jeff's bench/calibrate.py on gliformer-large-v1. Applies to
# probabilities, confidence and noul; the score expectation uses T=1.
DEFAULT_TEMPERATURE = 3.2

NOUL_YES = "yes"
NOUL_NO = "no"


@dataclass(frozen=True)
class Group:
  """Classification group; name and description carry instructions into the prompt."""

  key: str
  labels: tuple[str, ...]
  name: str | None = None
  description: str | None = None

  def __post_init__(self):
    if len(self.labels) != len(set(self.labels)):
      raise ValueError(f"group {self.key!r} has duplicate labels")


def build_group(key: str, question: Choice | Noul | Score) -> Group:
  """Bench question -> classification Group, matching jeff's server defaults."""
  name = question.instructions
  if isinstance(question, Noul):
    true_desc = question.criteria.get("true") if question.criteria else None
    false_desc = question.criteria.get("false") if question.criteria else None
    return Group(
      key=key,
      labels=(_fold(NOUL_YES, true_desc), _fold(NOUL_NO, false_desc)),
      name=name,
    )
  if isinstance(question, Choice):
    return Group(key=key, labels=_dedupe(tuple(_fold(k, d) for k, d in question.criteria.items())), name=name)
  # Score: the level descriptions themselves are the labels (jtr legend = index -> level).
  return Group(key=key, labels=_dedupe(tuple(question.criteria)), name=name)


def _fold(key: str, desc: str | None, sep: str = ": ") -> str:
  if desc:
    return f"{key}{sep}{desc}"
  return key


def _dedupe(labels: tuple[str, ...]) -> tuple[str, ...]:
  """Suffix duplicate labels so GLiFormer does not collapse their scores."""
  if len(set(labels)) == len(labels):
    return labels
  seen: dict[str, int] = {}
  out = []
  for label in labels:
    seen[label] = seen.get(label, 0) + 1
    out.append(label if seen[label] == 1 else f"{label} #{seen[label]}")
  return tuple(out)


def normalize(scores: list[float], temperature: float = 1.0) -> list[float]:
  """Normalize independent sigmoids; temperature > 1 flattens the distribution.

  This is score renormalization, not a calibrated posterior (jeff docstring).
  """
  s = [max(float(x), 0.0) for x in scores]
  if temperature != 1.0:
    s = [x ** (1.0 / temperature) for x in s]
  total = sum(s)
  if total <= EPS:
    return [1.0 / len(s)] * len(s)
  return [x / total for x in s]


def confidence(probs: list[float]) -> float:
  """Distribution peakedness: 0 for uniform, 1 for one-hot. jev does not publish its formula."""
  n = len(probs)
  if n < 2:
    return 1.0
  chance = 1.0 / n
  return round((max(probs) - chance) / (1.0 - chance), 4)
