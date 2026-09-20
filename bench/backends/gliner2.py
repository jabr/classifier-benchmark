"""GLiNER2 (fastino/gliner2-large-v1) backend via gliner2's Classifier."""

import os
import re
import time
from typing import Optional

from von.types import Choice, Noul, Score

from .base import Backend, Prediction

DEFAULT_MODEL_PATH = "models/fastino/gliner2-large-v1"


def _sanitize(text: str) -> str:
  # GLiNER2's compiler reserves structural markers and parentheses in prompts/labels;
  # a comma is a close-enough paraphrase of "(...)" for benchmark questions.
  return re.sub(r"\s*\(", ", ", text).replace(")", "")


class Gliner2Backend(Backend):
  name = "gliner2"
  description = f"GLiNER2 large, local ({DEFAULT_MODEL_PATH})"

  def __init__(
    self,
    model_path: str = DEFAULT_MODEL_PATH,
    device: Optional[str] = None,
  ):
    self.model_path = model_path
    self.device = device
    self.clf = None

  def warmup(self) -> float:
    from gliner2.classification.engine import Classifier

    t0 = time.perf_counter()
    self.clf = Classifier.from_pretrained(self.model_path, device=self.device)
    if self.device:
      # ClassificationScorer only records the device at load time; the model
      # must be moved explicitly or MPS runs mix CPU weights with MPS inputs.
      self.clf = self.clf.to(self.device)
    from gliner2.classification.schema import ClassificationSchema

    schema = ClassificationSchema().single("warmup", ["yes", "no"], instruction="warmup check")
    self.clf.classify("warmup warmup warmup", schema)
    self.load_seconds = time.perf_counter() - t0
    return self.load_seconds

  def _probabilities(self, state: str, name: str, labels: dict, instruction: str, exclusive: bool = True) -> dict:
    from gliner2.classification.schema import ClassificationSchema

    instruction = _sanitize(instruction)
    if isinstance(labels, dict):
      labels = {_sanitize(k): _sanitize(v) if isinstance(v, str) else v for k, v in labels.items()}
    else:
      labels = [_sanitize(label) for label in labels]
    if exclusive:
      schema = ClassificationSchema().single(name, labels, instruction=instruction)
    else:
      schema = ClassificationSchema().multi(name, labels, instruction=instruction)
    scores = self.clf.score(state, schema)
    return {label: scores.probability(name, label) for label in labels}

  @staticmethod
  def _level_from_label(label: str) -> str:
    return label.rsplit(" ", 1)[-1] if " " in label else label

  def predict_choice(self, state: str, question: Choice) -> Prediction:
    probabilities = self._probabilities(
      state,
      "decision",
      dict(question.criteria),
      question.instructions,
    )
    best = max(probabilities, key=probabilities.get)
    return Prediction(
      label=best,
      probabilities=probabilities,
      confidence=probabilities[best],
    )

  def predict_noul(self, state: str, question: Noul) -> Prediction:
    probabilities = self._probabilities(
      state,
      "judgment",
      ["yes", "no"],
      question.instructions,
    )
    probability = probabilities["yes"]
    best = max(probabilities, key=probabilities.get)
    return Prediction(
      label=best,
      probability=probability,
      probabilities=probabilities,
      confidence=max(probabilities.values()),
      raw=probability,
    )

  def predict_score(self, state: str, question: Score) -> Prediction:
    n = len(question.criteria)
    labels = {f"level {i}": desc for i, desc in enumerate(question.criteria)}
    probabilities = self._probabilities(
      state,
      "rating",
      labels,
      question.instructions,
    )
    remapped = {self._level_from_label(k): v for k, v in probabilities.items()}
    best = max(remapped, key=remapped.get)
    return Prediction(
      label=best,
      probabilities=remapped,
      confidence=remapped[best],
    )
