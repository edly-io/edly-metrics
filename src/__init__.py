from . import collectors  # noqa: F401 - ensure collectors register on import
from .registry import registry

__all__ = ["registry"]


