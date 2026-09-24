"""Laya (convaiinnovations/laya) backend via the native laya package."""

from pathlib import Path
from typing import Optional

from bench.cases import Choice, Noul, Score

from .base import Backend, Prediction, level_from_probabilities

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_DIR = REPO_ROOT / "models" / "convaiinnovations" / "laya"


class LayaBackend(Backend):
  name = "laya"

  def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None):
    self.device = device
    if model_path:
      self.model = model_path
    elif DEFAULT_MODEL_DIR.exists():
      self.model = str(DEFAULT_MODEL_DIR)
    else:
      self.model = "convaiinnovations/laya"
    model_dir = Path(self.model)
    # The checkpoint carries no version marker of its own; the laya package version
    # is the only durable provenance stamp for which generation was run.
    from importlib.metadata import version

    variant = model_dir.name if model_dir.name == "laya" else f"laya-{model_dir.name}"
    self.description = (
      f"{variant} {version('laya')}, local" if model_dir.exists() else f"{self.model} (HF registry)"
    )

  def warmup(self) -> float:
    import time

    from laya import load

    t0 = time.perf_counter()
    self.agent = load(self.model, device=self.device)
    self.agent.system_one("warmup", {"q": {"type": "noul", "instructions": "Warm up"}})
    return time.perf_counter() - t0

  def _ask(self, state: str, question: dict) -> dict:
    response = self.agent.system_one(state, {"q": question})
    return response["answers"]["q"]

  def predict_choice(self, state: str, question: Choice) -> Prediction:
    answer = self._ask(
      state,
      {"type": "choice", "instructions": question.instructions, "criteria": dict(question.criteria)},
    )
    return Prediction(
      label=answer["choice"],
      probabilities=dict(answer["probabilities"]),
      confidence=answer["confidence"],
    )

  def predict_noul(self, state: str, question: Noul) -> Prediction:
    payload = {"type": "noul", "instructions": question.instructions}
    if question.criteria:
      payload["criteria"] = dict(question.criteria)
    probability = self._ask(state, payload)["noul"]
    return Prediction(
      label="yes" if probability >= 0.5 else "no",
      probability=probability,
      confidence=abs(probability - 0.5) * 2,
      raw=probability,
    )

  def predict_score(self, state: str, question: Score) -> Prediction:
    answer = self._ask(
      state,
      {"type": "score", "instructions": question.instructions, "criteria": list(question.criteria)},
    )
    probabilities = dict(answer["probabilities"])
    label = level_from_probabilities(probabilities, len(question.criteria))
    return Prediction(
      label=label,
      probabilities=probabilities,
      confidence=answer["confidence"],
      raw=answer["score"],
    )
