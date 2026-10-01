"""Decima (amyrmahdy/decima-small) backend via the decima package: int8 ONNX on one CPU thread.

Questions go through Decima's own System One adapter (`decima.systemone.system_one`), which takes the
bench's wire shape as is, so nothing here is tuned to this benchmark.
"""

from typing import Optional

from bench.cases import Choice, Noul, Score

from .base import Backend, Prediction


class DecimaBackend(Backend):
  name = "decima"

  def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None, precision: str = "int8"):
    self.model = model_path or "amyrmahdy/decima-small"
    self.precision = precision
    self.description = f"{self.model} ({precision} ONNX, 1 CPU thread)"

  def warmup(self) -> float:
    import time

    from decima import Decima
    from decima.systemone import system_one

    t0 = time.perf_counter()
    self.decima = Decima.from_pretrained(self.model, precision=self.precision)
    self.system_one = system_one
    self._ask("warmup", {"type": "noul", "instructions": "Warm up"})
    return time.perf_counter() - t0

  def _ask(self, state: str, question: dict) -> dict:
    return self.system_one(self.decima, state, {"q": question})["q"]

  def predict_choice(self, state: str, question: Choice) -> Prediction:
    answer = self._ask(state, {"type": "choice", "instructions": question.instructions, "criteria": dict(question.criteria)})
    return Prediction(label=answer["choice"], probabilities=answer["probabilities"], confidence=answer["confidence"])

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
    answer = self._ask(state, {"type": "score", "instructions": question.instructions, "criteria": list(question.criteria)})
    probabilities = answer["probabilities"]
    label = max(probabilities, key=probabilities.get)
    return Prediction(label=label, probabilities=probabilities, confidence=answer["confidence"], raw=answer["score"])
