"""Specifications for the Customer bounded context.

Reusable business predicates that evaluate a Customer aggregate root.
They carry no mutation logic and depend purely on domain state.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from .entities import Customer
from .enums import CustomerStatus

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
class IsActiveCustomerSpecification(Specification[Customer]):
    """Satisfied when a customer is in ACTIVE status."""

    def is_satisfied_by(self, candidate: Customer) -> bool:
        return candidate.status == CustomerStatus.ACTIVE


@dataclass(frozen=True, slots=True)
class IsInactiveCustomerSpecification(Specification[Customer]):
    """Satisfied when a customer is in INACTIVE status."""

    def is_satisfied_by(self, candidate: Customer) -> bool:
        return candidate.status == CustomerStatus.INACTIVE


@dataclass(frozen=True, slots=True)
class CanUpdateCustomerSpecification(Specification[Customer]):
    """Satisfied when a customer account is eligible for profile updates."""

    def is_satisfied_by(self, candidate: Customer) -> bool:
        return candidate.status != CustomerStatus.ARCHIVED


@dataclass(frozen=True, slots=True)
class CanDeactivateCustomerSpecification(Specification[Customer]):
    """Satisfied when a customer account can be deactivated."""

    def is_satisfied_by(self, candidate: Customer) -> bool:
        return candidate.status in (CustomerStatus.ACTIVE, CustomerStatus.SUSPENDED)


@dataclass(frozen=True, slots=True)
class HasValidContactInformationSpecification(Specification[Customer]):
    """Satisfied when a customer has a valid contact phone number."""

    def is_satisfied_by(self, candidate: Customer) -> bool:
        return bool(candidate.phone and candidate.phone.value)
