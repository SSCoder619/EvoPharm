"""Application-layer result abstraction.

Provides a strongly-typed container for returning application use-case execution results
without relying on HTTP status codes or web framework dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class ApplicationResult(Generic[T]):
    """Immutable result container representing the outcome of an application use case."""

    is_success: bool
    _value: T | None = None
    error_message: str | None = None
    error_code: str | None = None

    @classmethod
    def success(cls, value: T | None = None) -> "ApplicationResult[T]":
        """Construct a successful application result with optional payload value."""
        return cls(is_success=True, _value=value)

    @classmethod
    def failure(cls, error_message: str, error_code: str = "APPLICATION_ERROR") -> "ApplicationResult[T]":
        """Construct a failed application result with an error message and code."""
        return cls(is_success=False, error_message=error_message, error_code=error_code)

    @property
    def is_failure(self) -> bool:
        return not self.is_success

    @property
    def value(self) -> T:
        """Access payload value. Raises ValueError if accessing value on a failed result."""
        if not self.is_success:
            raise ValueError(f"Cannot access value on a failed ApplicationResult: {self.error_message}")
        return self._value  # type: ignore[return-value]
