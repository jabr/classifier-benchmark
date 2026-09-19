"""Von (wfzyx/von-1.0) backend via the native von package."""

from typing import Optional

import von
from von.types import Choice, Noul, Score

from .base import Backend, Prediction

BACKEND_ALIASES = ("modernbert", "von", "von-1.0")


def _level_from_probabilities(probabilities: dict[str, float], n: int) -> str:
  for key in probabilities:
    try:
      idx = int(key)
    except (TypeError, ValueError):
      continue
    if 0 <= idx < n:
      best = max(probabilities, key=lambda k: probabilities[k])
      return str(int(best))
  return "0"


class VonBackend(Backend):
  name = "von"
  description = "von-1.0 ModernBERT, local"

  def __init__(self, backend: str = "modernbert", device: Optional[str] = None):
    self.backend = backend
    self.device = device

  def warmup(self) -> float:
    import time

    t0 = time.perf_counter()
    from von.engine import VonEngine

    VonEngine.set_backend(self.backend, device=self.device)
    von.judge("warmup warmup", instructions="Device warm up")
    return time.perf_counter() - t0

  def predict_choice(self, state: str, question: Choice) -> Prediction:
    answer = von.decide(
      state,
      choices=dict(question.criteria),
      instructions=question.instructions,
    )
    return Prediction(
      label=answer.choice,
      probabilities=dict(answer.probabilities),
      confidence=answer.confidence,
    )

  def predict_noul(self, state: str, question: Noul) -> Prediction:
    probability = von.judge(state, instructions=question.instructions)
    return Prediction(
      label="yes" if probability >= 0.5 else "no",
      probability=probability,
      confidence=abs(probability - 0.5) * 2,
      raw=probability,
    )

  def predict_score(self, state: str, question: Score) -> Prediction:
    answer = von.rate(
      state,
      criteria=list(question.criteria),
      instructions=question.instructions,
    )
    probabilities = dict(answer.probabilities)
    label = _level_from_probabilities(probabilities, len(question.criteria))
    return Prediction(
      label=label,
      probabilities=probabilities,
      confidence=answer.confidence,
      raw=answer.score,
    )
