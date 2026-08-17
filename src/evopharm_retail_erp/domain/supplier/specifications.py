"""Specifications for the Supplier bounded context.

Reusable business predicates that evaluate a Supplier aggregate root.
They carry no mutation logic and depend purely on domain state.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from .entities import Supplier
from .enums import SupplierStatus

CandidateT = TypeVar("CandidateT")


class Specification(ABC, Generic[CandidateT]):
    """Abstract base class for composable business specifications."""

    @abstractmethod
    def is_satisfied_by(self, candidate: CandidateT) -> bool:
        """Evaluate predicate against a candidate object."""

    def __and__(self, other: Specification[CandidateT]) -> Specification[CandidateT]:
        return AndSpecification(self, other)

    def __or__(self, other: Specification[CandidateT]) -> Specification[CandidateT]:
        return OrSpecification(self, other)

    def __invert__(self) -> Specification[CandidateT]:
        return NotSpecification(self)


@dataclass(frozen=True, slots=True)
class AndSpecification(Specification[CandidateT]):
    left: Specification[CandidateT]
    right: Specification[CandidateT]

    def is_satisfied_by(self, candidate: CandidateT) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)


@dataclass(frozen=True, slots=True)
class OrSpecification(Specification[CandidateT]):
    left: Specification[CandidateT]
    right: Specification[CandidateT]

    def is_satisfied_by(self, candidate: CandidateT) -> bool:
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)


@dataclass(frozen=True, slots=True)
class NotSpecification(Specification[CandidateT]):
    spec: Specification[CandidateT]

    def is_satisfied_by(self, candidate: CandidateT) -> bool:
        return not self.spec.is_satisfied_by(candidate)


@dataclass(frozen=True, slots=True)
class IsActiveSupplierSpecification(Specification[Supplier]):
    """Satisfied when a supplier is in ACTIVE status."""

    def is_satisfied_by(self, candidate: Supplier) -> bool:
        return candidate.status == SupplierStatus.ACTIVE


@dataclass(frozen=True, slots=True)
class IsInactiveSupplierSpecification(Specification[Supplier]):
    """Satisfied when a supplier is in INACTIVE status."""

    def is_satisfied_by(self, candidate: Supplier) -> bool:
        return candidate.status == SupplierStatus.INACTIVE


@dataclass(frozen=True, slots=True)
class IsSuspendedSupplierSpecification(Specification[Supplier]):
    """Satisfied when a supplier is in SUSPENDED status."""

    def is_satisfied_by(self, candidate: Supplier) -> bool:
        return candidate.status == SupplierStatus.SUSPENDED


@dataclass(frozen=True, slots=True)
class CanPurchaseFromSupplierSpecification(Specification[Supplier]):
    """Satisfied when a supplier is eligible to receive purchase orders."""

    def is_satisfied_by(self, candidate: Supplier) -> bool:
        return candidate.status == SupplierStatus.ACTIVE


@dataclass(frozen=True, slots=True)
class CanDeactivateSupplierSpecification(Specification[Supplier]):
    """Satisfied when a supplier can be deactivated."""

    def is_satisfied_by(self, candidate: Supplier) -> bool:
        return candidate.status in (SupplierStatus.ACTIVE, SupplierStatus.SUSPENDED)


@dataclass(frozen=True, slots=True)
class HasValidTaxRegistrationSpecification(Specification[Supplier]):
    """Satisfied when a supplier has registered both GSTIN and PAN details."""

    def is_satisfied_by(self, candidate: Supplier) -> bool:
        return candidate.is_tax_compliant
