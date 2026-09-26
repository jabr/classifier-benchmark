from typing import Callable

from .base import Backend


def create_backend(name: str, **kwargs) -> Backend:
  if name == "von":
    from .von import VonBackend

    return VonBackend(**kwargs)
  if name == "jev":
    from .jev import JevBackend

    return JevBackend(**kwargs)
  if name == "jeff":
    from .jeff import JeffBackend

    return JeffBackend(**kwargs)
  if name == "gliner2":
    from .gliner2 import Gliner2Backend

    return Gliner2Backend(**kwargs)
  if name == "gliner25-decide":
    from .gliner25_decide import Gliner25DecideBackend

    return Gliner25DecideBackend(**kwargs)
  if name == "laya":
    from .laya import LayaBackend

    return LayaBackend(**kwargs)
  raise ValueError(
    f"Unknown backend '{name}'. Available: von, jev, jeff, gliner2, gliner25-decide, laya"
  )


BACKEND_FACTORIES: dict[str, Callable[[], Backend]] = {
  "von": lambda **kw: create_backend("von", **kw),
  "jev": lambda **kw: create_backend("jev", **kw),
  "gliner2": lambda **kw: create_backend("gliner2", **kw),
}
