"""Application-layer exception hierarchy.

Every exception here is raised by use-case handlers or application services when an
orchestration, permission, input validation, or resource lookup rule is violated.
None of these exceptions represent domain aggregate invariant violations or raw database infrastructure errors.
"""
from __future__ import annotations


class ApplicationError(Exception):
    """Base class for all application-layer orchestration errors."""

    def __init__(self, message: str, code: str = "APPLICATION_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class ApplicationValidationError(ApplicationError):
    """Raised when application input DTOs or commands fail application-level validation."""

    def __init__(self, message: str, field: str | None = None) -> None:
        self.field = field
        super().__init__(message, code="APPLICATION_VALIDATION_ERROR")


class ResourceNotFoundError(ApplicationError):
    """Raised when a required aggregate resource is not found by an application handler."""

    def __init__(self, resource_type: str, identifier: object) -> None:
        self.resource_type = resource_type
        self.identifier = identifier
        super().__init__(
            f"{resource_type} with identifier {identifier!r} was not found",
            code="RESOURCE_NOT_FOUND",
        )


class ConflictError(ApplicationError):
    """Raised when an application operation conflicts with existing system state."""

    def __init__(self, message: str, code: str = "CONFLICT_ERROR") -> None:
        super().__init__(message, code=code)


class ConcurrencyError(ConflictError):
    """Raised when an optimistic concurrency version conflict occurs during persistence."""

    def __init__(self, resource_type: str, identifier: object, expected_version: int) -> None:
        self.resource_type = resource_type
        self.identifier = identifier
        self.expected_version = expected_version
        super().__init__(
            f"Concurrency conflict for {resource_type} {identifier!r}: expected version {expected_version}",
            code="CONCURRENCY_CONFLICT",
        )


class UnauthorizedError(ApplicationError):
    """Raised when an unauthenticated caller attempts an application use case."""

    def __init__(self, message: str = "Authentication credentials missing or invalid") -> None:
        super().__init__(message, code="UNAUTHORIZED")


class ForbiddenError(ApplicationError):
    """Raised when an authenticated caller lacks required permissions for a use case."""

    def __init__(self, message: str = "Insufficient permissions for requested operation") -> None:
        super().__init__(message, code="FORBIDDEN")
