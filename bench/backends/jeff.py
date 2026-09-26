"""jeff backend, in-process (logan-markewich/jeff) — Jev rebuild on GLiFormer 400M.

jeff's server is infrastructure; the model is a plain GLiFormer checkpoint
loaded through the `gliformer` package (DeBERTa-v3-large encoder in
transformers), so this backend runs it in-process: one encoder pass per
question, raw per-label sigmoids from gliformer, then jeff's prompt/decode
layer (vendored in _jeff_core, server defaults). Weights:

    just download knowledgator/gliformer-large-v1
"""

from pathlib import Path
from typing import Optional

import torch

from bench.cases import Choice, Noul, Score

from ._jeff_core import (
    DEFAULT_TEMPERATURE,
    Group,
    build_group,
    confidence,
    normalize,
)
from .base import Backend, Prediction

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_DIR = REPO_ROOT / "models" / "knowledgator" / "gliformer-large-v1"
DEFAULT_MODEL_PATH = str(DEFAULT_MODEL_DIR)

# The decoder treats 0.0 as unset; a negative threshold returns every label.
ALL_LABELS_THRESHOLD = -1.0


class JeffBackend(Backend):
  name = "jeff"
  description = f"jeff (logan-markewich/jeff, GLiFormer large 576M) local in-process ({DEFAULT_MODEL_PATH})"

  def __init__(
    self,
    model_path: Optional[str] = None,
    device: Optional[str] = None,
    temperature: float = DEFAULT_TEMPERATURE,
  ):
    # The checkpoint config asks for flash attention; only cuda can run it,
    # so non-cuda loads force the eager kernel (same as jeff's TorchBackend).
    self.device = device or _default_device()
    self.model_path = model_path or (str(DEFAULT_MODEL_DIR) if DEFAULT_MODEL_DIR.exists() else "knowledgator/gliformer-large-v1")
    self.temperature = temperature
    self.model = None

  def warmup(self) -> float:
    import time

    try:
      from gliformer import GLiFormer
    except ModuleNotFoundError as exc:
      raise RuntimeError(
        "jeff backend needs its optional dependency group: uv sync --extra jeff"
      ) from exc

    t0 = time.perf_counter()
    kwargs = {"_attn_implementation": "flash" if self.device == "cuda" else "eager"}
    with warnings_catch_eager():
      self.model = GLiFormer.from_pretrained(self.model_path, map_location=self.device, **kwargs)
    if self.device != "cuda":
      _set_attn_kernel(self.model.model, "eager")
    self.model.to(self.device).eval()

    from gliformer.gliformer import resolve_gliformer_collator_class

    collator_cls = self.model.data_collator_class or resolve_gliformer_collator_class(self.model.config)
    self._collator = collator_cls(
      self.model.config,
      data_processor=self.model.data_processor,
      return_tokens=True,
      prepare_labels=False,
    )
    self.check = build_group(
      "warmup", Score(instructions="warmup check", criteria=["low", "high"])
    )
    self._score("warmup warmup warmup", self.check)
    self.load_seconds = time.perf_counter() - t0
    return self.load_seconds

  def _score(self, state: str, group: Group) -> list[float]:
    """One text, one group -> raw per-label sigmoids (jeff TorchBackend.score)."""
    from torch.utils.data import DataLoader

    tokens, _, _ = self.model.prepare_inputs([state])
    items = [
      {
        "tokenized_text": toks,
        "classification": [
          {
            "name": group.name,
            "description": group.description,
            "all_labels": list(group.labels),
            "true_labels": [],
          }
        ],
      }
      for toks in tokens
    ]
    loader = DataLoader(items, batch_size=1, collate_fn=self._collator)
    decoded, _ = self.model._process_multitask_batches(loader, ALL_LABELS_THRESHOLD, True, True, decoder_kwargs=None)
    # decoded["classification"] is [text][group] -> label dicts; one group per call here.
    preds = decoded["classification"][0][0]
    by_name = {p["class_name"]: float(p["score"]) for p in preds}
    return [by_name.get(label, 0.0) for label in group.labels]

  def predict_choice(self, state: str, question: Choice) -> Prediction:
    group = build_group("decision", question)
    probabilities = {
      option: prob
      for option, prob in zip(question.criteria, normalize(self._score(state, group), self.temperature))
    }
    label = max(probabilities, key=probabilities.get)
    return Prediction(
      label=label,
      probabilities=probabilities,
      confidence=confidence(list(probabilities.values())),
    )

  def predict_noul(self, state: str, question: Noul) -> Prediction:
    group = build_group("judgment", question)
    probabilities = {
      lab: prob
      for lab, prob in zip(("yes", "no"), normalize(self._score(state, group), self.temperature))
    }
    probability = probabilities["yes"]
    return Prediction(
      label="yes" if probability >= 0.5 else "no",
      probability=probability,
      probabilities=probabilities,
      confidence=abs(probability - 0.5) * 2,
      raw=probability,
    )

  def predict_score(self, state: str, question: Score) -> Prediction:
    group = build_group("rating", question)
    raw = self._score(state, group)
    probs = normalize(raw, self.temperature)
    probabilities = {str(i): p for i, p in enumerate(probs)}
    # Tempering increases score MAE in jeff; the score is the raw (T=1) expectation,
    # while the argmax label follows the tempered probabilities (same ordering).
    score = sum(i * p for i, p in enumerate(normalize(raw)))
    label = str(max(probabilities, key=probabilities.get))
    return Prediction(
      label=label,
      probabilities=probabilities,
      confidence=confidence(probs),
      raw=score,
    )


def _default_device() -> str:
  if torch.cuda.is_available():
    return "cuda"
  if torch.backends.mps.is_available():
    return "mps"
  return "cpu"


def _set_attn_kernel(root, kernel: str) -> None:
  for m in root.modules():
    if hasattr(m, "attn_kernel"):
      m.attn_kernel = kernel


class warnings_catch_eager:
  """gliformer warns about the flash fallback even when eager was requested."""

  def __enter__(self):
    import warnings

    self._ctx = warnings.catch_warnings()
    self._ctx.__enter__()
    warnings.filterwarnings("ignore", message=r"attn_kernel=.*flashdeberta")
    return self

  def __exit__(self, *exc):
    return self._ctx.__exit__(*exc)
