"""GLiNER2.5-Decide (fastino/GLiNER2.5-Decide) backend, 340M decision-tuned
fine-tune of gliner2-large-v1 for operational decisions.

Same span architecture and prompt format as gliner2-large-v1, so it loads
through the same gliner2 Classifier interface as the GLiNER2-large backend —
the card's classify_text API compiles to the identical model schema (verified
in gliner2 2.0.0; only an inert class_act field differs, which the processor
never reads).
"""

from typing import Optional

from .gliner2 import Gliner2Backend

DEFAULT_MODEL_PATH = "models/fastino/GLiNER2.5-Decide"


class Gliner25DecideBackend(Gliner2Backend):
  name = "gliner25-decide"
  description = f"GLiNER2.5-Decide, local ({DEFAULT_MODEL_PATH})"

  def __init__(self, model_path: str = DEFAULT_MODEL_PATH, device: Optional[str] = None):
    super().__init__(model_path=model_path, device=device)
