"""Jev (typesafe) backend, served via OpenRouter as typesafe/jev-1.13.

OpenRouter exposes Jev as a decisions model on /api/alpha/decisions,
which accepts the benchmark's System One question schema (bench.cases).
"""

import json
import os
import urllib.error
import urllib.request
from typing import Optional

from bench.cases import Choice, Noul, Question, Score, question_payload

from .base import Backend, Prediction

DEFAULT_MODEL = "typesafe/jev-1.13"
DEFAULT_BASE_URL = "https://openrouter.ai/api/alpha/decisions"


class JevBackend(Backend):
  name = "jev"
  description = f"typesafe Jev via OpenRouter ({DEFAULT_MODEL})"

  def __init__(
    self,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
    base_url: str = DEFAULT_BASE_URL,
    max_attempts: int = 3,
  ):
    self.model = model
    self.base_url = base_url
    self.api_key = (
      api_key
      or os.environ.get("OPENROUTER_API_KEY")
      or os.environ.get("SANDBOX_OPENROUTER_API_KEY")
    )
    if not self.api_key:
      raise RuntimeError(
        "Neither OPENROUTER_API_KEY nor SANDBOX_OPENROUTER_API_KEY is set. "
        "Get a key at https://openrouter.ai/keys and export it before running "
        "the jev backend."
      )
    self.max_attempts = max_attempts

  def _questions(self, name: str, question: Question) -> dict:
    return {name: question_payload(question)}

  def _invoke(self, name: str, question: Question, state: str) -> tuple[dict, dict]:
    body = json.dumps(
      {
        "model": self.model,
        "state": state,
        "questions": self._questions(name, question),
      }
    ).encode()
    request = urllib.request.Request(
      self.base_url,
      data=body,
      headers={
        "Authorization": f"Bearer {self.api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/wfzyx/von",
        "X-Title": "von-benchmark",
      },
      method="POST",
    )
    last_error: Optional[Exception] = None
    for attempt in range(self.max_attempts):
      try:
        with urllib.request.urlopen(request, timeout=120) as response:
          data = json.loads(response.read().decode())
        return data["answers"][name], data.get("usage", {})
      except (urllib.error.URLError, KeyError, json.JSONDecodeError, TimeoutError) as exc:
        last_error = exc
    raise RuntimeError(
      f"OpenRouter decisions request failed after {self.max_attempts} attempts: {last_error}"
    )

  def predict_choice(self, state: str, question: Choice) -> Prediction:
    answer, _ = self._invoke("decision", question, state)
    probabilities = {str(k): float(v) for k, v in answer.get("probabilities", {}).items()}
    label = answer.get("choice")
    if label is None and probabilities:
      label = max(probabilities, key=probabilities.get)
    if label is None:
      raise ValueError(f"Jev returned no choice: {answer}")
    return Prediction(
      label=str(label),
      probabilities=probabilities or None,
      confidence=answer.get("confidence"),
    )

  def predict_noul(self, state: str, question: Noul) -> Prediction:
    answer, _ = self._invoke("judgment", question, state)
    if "noul" in answer:
      probability = float(answer["noul"])
    else:
      raise ValueError(f"Jev returned no noul value: {answer}")
    return Prediction(
      label="yes" if probability >= 0.5 else "no",
      probability=probability,
      raw=probability,
    )

  def predict_score(self, state: str, question: Score) -> Prediction:
    answer, _ = self._invoke("rating", question, state)
    probabilities = {str(k): float(v) for k, v in answer.get("probabilities", {}).items()}
    n = len(question.criteria)
    label = None
    if probabilities:
      best = max(probabilities, key=probabilities.get)
      try:
        label = str(int(float(best)))
      except ValueError:
        label = None
    if label is None:
      raw = float(answer.get("score", 0))
      label = str(max(0, min(n - 1, round(raw))))
    return Prediction(
      label=label,
      probabilities=probabilities or None,
      confidence=answer.get("confidence"),
      raw=answer.get("score"),
    )
