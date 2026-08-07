"""
Specification Pattern implementations for the Medicine bounded context in EvoPharm Retail ERP.

Provides reusable, stateless, immutable business predicates for filtering and
evaluating Medicine domain entities in accordance with Domain-Driven Design (DDD).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from evopharm_retail_erp.domain.medicine.entities import Medicine

T = TypeVar("T")


class Specification(ABC, Generic[T]):
    """
    Abstract Base Specification supporting composite operations (&, |, ~).

    Encapsulates a business predicate that can be evaluated against a domain candidate object.
    """

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        """Evaluate whether the candidate satisfies the specification logic."""
        ...

    def __and__(self, other: Specification[T]) -> Specification[T]:
        return AndSpecification(self, other)

    def __or__(self, other: Specification[T]) -> Specification[T]:
        return OrSpecification(self, other)

    def __invert__(self) -> Specification[T]:
        return NotSpecification(self)


@dataclass(frozen=True, slots=True)
class AndSpecification(Specification[T]):
    """Composite specification representing logical AND of two specifications."""

    left: Specification[T]
    right: Specification[T]

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)


@dataclass(frozen=True, slots=True)
class OrSpecification(Specification[T]):
    """Composite specification representing logical OR of two specifications."""

    left: Specification[T]
    right: Specification[T]

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)


@dataclass(frozen=True, slots=True)
class NotSpecification(Specification[T]):
    """Composite specification representing logical NOT of a specification."""

    spec: Specification[T]

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self.spec.is_satisfied_by(candidate)


@dataclass(frozen=True, slots=True)
class IsControlledMedicineSpecification(Specification[Medicine]):
    """Evaluates whether a medicine is categorized as a controlled substance requiring regulatory oversight."""

    def is_satisfied_by(self, candidate: Medicine) -> bool:
        return candidate.is_controlled


@dataclass(frozen=True, slots=True)
class IsPrescriptionMedicineSpecification(Specification[Medicine]):
    """Evaluates whether a medicine requires a practitioner's prescription to dispense."""

    def is_satisfied_by(self, candidate: Medicine) -> bool:
        return candidate.requires_prescription


@dataclass(frozen=True, slots=True)
class IsSaleableMedicineSpecification(Specification[Medicine]):
    """Evaluates whether a medicine is active and currently eligible for sale."""

    def is_satisfied_by(self, candidate: Medicine) -> bool:
        return candidate.is_saleable


@dataclass(frozen=True, slots=True)
class IsDiscontinuedMedicineSpecification(Specification[Medicine]):
    """Evaluates whether a medicine product line has been discontinued."""

    def is_satisfied_by(self, candidate: Medicine) -> bool:
        return candidate.is_discontinued


@dataclass(frozen=True, slots=True)
class HasBarcodeSpecification(Specification[Medicine]):
    """Evaluates whether a medicine has registered barcodes, optionally matching a specific code."""

    target_barcode: str | None = None

    def is_satisfied_by(self, candidate: Medicine) -> bool:
        if not candidate.barcodes:
            return False

        if self.target_barcode is None:
            return True

        return any(
            str(b) == self.target_barcode or b.value == self.target_barcode
            for b in candidate.barcodes
        )


@dataclass(frozen=True, slots=True)
class HasAlternateNamesSpecification(Specification[Medicine]):
    """Evaluates whether a medicine has recorded alternate, generic, or brand aliases."""

    def is_satisfied_by(self, candidate: Medicine) -> bool:
        return bool(candidate.alternate_names)