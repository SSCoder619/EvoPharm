"""Application-layer common foundation exports."""
from __future__ import annotations

from .exceptions import (
    ApplicationError,
    ApplicationValidationError,
    ConcurrencyError,
    ConflictError,
    ForbiddenError,
    ResourceNotFoundError,
    UnauthorizedError,
)
from .ports import (
    ClockPort,
    EventDispatcherPort,
    IdGeneratorPort,
)
from .result import ApplicationResult
from .unit_of_work import UnitOfWork

__all__ = [
    "UnitOfWork",
    "ApplicationResult",
    "ApplicationError",
    "ApplicationValidationError",
    "ResourceNotFoundError",
    "ConflictError",
    "ConcurrencyError",
    "UnauthorizedError",
    "ForbiddenError",
    "ClockPort",
    "IdGeneratorPort",
    "EventDispatcherPort",
]
