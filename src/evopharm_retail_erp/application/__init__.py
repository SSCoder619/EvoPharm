"""Application-layer contracts and foundation components."""
from __future__ import annotations

from .common import (
    ApplicationError,
    ApplicationResult,
    UnitOfWork,
)

__all__ = [
    "ApplicationError",
    "ApplicationResult",
    "UnitOfWork",
]
