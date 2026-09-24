"""Von 1.2 backend via the native von-sdk package (Option-Marker joint attention)."""

from pathlib import Path
from typing import Optional

import von
from bench.cases import Choice, Noul, Score

from .base import Backend, Prediction, level_from_probabilities

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_DIR = REPO_ROOT / "models" / "wfzyx" / "von"


class VonBackend(Backend):
  name = "von"

  def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None):
    self.device = device
    self.checkpoint_dir = model_path or (str(DEFAULT_MODEL_DIR) if DEFAULT_MODEL_DIR.exists() else None)
    self.description = (
      "von-1.2, local" if self.checkpoint_dir else "von-1.2 (HF registry: wfzyx/von)"
    )

  def warmup(self) -> float:
    import time

    t0 = time.perf_counter()
    from von.backends.option_marker_backend import OptionMarkerBackend
    from von.engine import VonEngine

    # VonEngine wires only its own default checkpoint locations, so replace the
    # backend with a path-pinned OptionMarkerBackend and install the engine as
    # the singleton the module-level von API resolves.
    engine = VonEngine(backend_name="von-1.2", device=self.device)
    if self.checkpoint_dir:
      engine.backend = OptionMarkerBackend(checkpoint_dir=self.checkpoint_dir, device=self.device)
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
    probability = von.judge(
      state,
      instructions=question.instructions,
      criteria=dict(question.criteria) if question.criteria else None,
    )
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
