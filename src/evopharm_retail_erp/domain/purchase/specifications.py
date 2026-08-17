"""Specifications for the Purchase bounded context.

Reusable business predicates that evaluate a Purchase aggregate or line entity.
They carry no mutation logic and depend purely on domain state.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from .entities import Purchase, PurchaseLine
from .enums import PurchaseStatus, ReceivingStatus

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
class IsPurchaseDraftSpecification(Specification[Purchase]):
    """Satisfied when a purchase order is in DRAFT status."""

    def is_satisfied_by(self, candidate: Purchase) -> bool:
        return candidate.purchase_status == PurchaseStatus.DRAFT


@dataclass(frozen=True, slots=True)
class IsPurchaseApprovedSpecification(Specification[Purchase]):
    """Satisfied when a purchase order has been APPROVED."""

    def is_satisfied_by(self, candidate: Purchase) -> bool:
        return candidate.purchase_status == PurchaseStatus.APPROVED


@dataclass(frozen=True, slots=True)
class IsPurchaseOrderedSpecification(Specification[Purchase]):
    """Satisfied when a purchase order has been ORDERED from supplier."""

    def is_satisfied_by(self, candidate: Purchase) -> bool:
        return candidate.purchase_status == PurchaseStatus.ORDERED


@dataclass(frozen=True, slots=True)
class IsPurchaseReceivedSpecification(Specification[Purchase]):
    """Satisfied when a purchase order has been fully RECEIVED."""

    def is_satisfied_by(self, candidate: Purchase) -> bool:
        return candidate.purchase_status == PurchaseStatus.RECEIVED


@dataclass(frozen=True, slots=True)
class IsPurchaseCancelledSpecification(Specification[Purchase]):
    """Satisfied when a purchase order is CANCELLED."""

    def is_satisfied_by(self, candidate: Purchase) -> bool:
        return candidate.purchase_status == PurchaseStatus.CANCELLED


@dataclass(frozen=True, slots=True)
class CanReceivePurchaseSpecification(Specification[Purchase]):
    """Satisfied when a purchase order is eligible to receive incoming stock."""

    def is_satisfied_by(self, candidate: Purchase) -> bool:
        return candidate.purchase_status in (
            PurchaseStatus.ORDERED,
            PurchaseStatus.PARTIALLY_RECEIVED,
        ) and candidate.receiving_status != ReceivingStatus.COMPLETED


@dataclass(frozen=True, slots=True)
class CanCancelPurchaseSpecification(Specification[Purchase]):
    """Satisfied when a purchase order can be cancelled."""

    def is_satisfied_by(self, candidate: Purchase) -> bool:
        return candidate.purchase_status not in (
            PurchaseStatus.RECEIVED,
            PurchaseStatus.CANCELLED,
            PurchaseStatus.REJECTED,
        ) and candidate.receiving_status != ReceivingStatus.COMPLETED


@dataclass(frozen=True, slots=True)
class HasOutstandingQuantitySpecification(Specification[PurchaseLine]):
    """Satisfied when a purchase line has unreceived outstanding quantity."""

    def is_satisfied_by(self, candidate: PurchaseLine) -> bool:
        return candidate.outstanding_quantity.is_positive() and not candidate.is_cancelled
