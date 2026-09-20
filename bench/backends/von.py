"""Von backend via the native von-sdk package."""

from pathlib import Path
from typing import Optional

import von
from von.types import Choice, Noul, Score

from .base import Backend, Prediction, level_from_probabilities

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_DIR = REPO_ROOT / "models" / "wfzyx" / "von-1.0"


class VonBackend(Backend):
  name = "von"

  def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None):
    self.device = device
    if model_path:
      self.model = model_path
    elif DEFAULT_MODEL_DIR.exists():
      self.model = str(DEFAULT_MODEL_DIR)
    else:
      self.model = "von-1.0"
    model_dir = Path(self.model)
    self.description = f"{model_dir.name}, local" if model_dir.exists() else f"{self.model} (HF registry)"

  def warmup(self) -> float:
    import time

    t0 = time.perf_counter()
    from von.backends.berta_backend import BertaBackend
    from von.engine import VonEngine

    # VonEngine.set_backend only accepts fixed registry aliases, so install a
    # BertaBackend directly to honor arbitrary local model paths.
    engine = VonEngine.__new__(VonEngine)
    engine.backend_name = "model-path"
    engine.device = self.device
    engine.backend = BertaBackend(variant=self.model, device=self.device)
    VonEngine._instance = engine
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
    label = level_from_probabilities(probabilities, len(question.criteria))
    return Prediction(
      label=label,
      probabilities=probabilities,
      confidence=answer.confidence,
      raw=answer.score,
    )
