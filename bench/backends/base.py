"""Backend abstraction: one class per classification model, same case schema."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from bench.cases import Choice, Noul, Score


@dataclass
class Prediction:
  label: str
  probability: Optional[float] = None
  probabilities: Optional[dict[str, float]] = None
  confidence: Optional[float] = None
  raw: Optional[float] = None


def level_from_probabilities(probabilities: dict[str, float], n: int) -> str:
  for key in probabilities:
    try:
      idx = int(key)
    except (TypeError, ValueError):
      continue
    if 0 <= idx < n:
      best = max(probabilities, key=lambda k: probabilities[k])
      return str(int(best))
  return "0"


class Backend(ABC):
  name: str = "abstract"
  description: str = ""

  def warmup(self) -> float:
    """Prepare the model for inference; returns load time in seconds."""
    return 0.0

  @abstractmethod
  def predict_choice(self, state: str, question: Choice) -> Prediction: ...

  @abstractmethod
  def predict_noul(self, state: str, question: Noul) -> Prediction: ...

  @abstractmethod
  def predict_score(self, state: str, question: Score) -> Prediction: ...
