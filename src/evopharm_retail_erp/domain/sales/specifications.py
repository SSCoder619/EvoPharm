"""Specifications for the Sales bounded context.

Reusable business predicates that evaluate a Sale aggregate or line entity.
They carry no mutation logic and depend purely on domain state.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from .entities import Sale, SaleLine
from .enums import PaymentStatus, SaleStatus

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
class IsSaleDraftSpecification(Specification[Sale]):
    """Satisfied when a sale is in DRAFT status."""

    def is_satisfied_by(self, candidate: Sale) -> bool:
        return candidate.sale_status == SaleStatus.DRAFT


@dataclass(frozen=True, slots=True)
class IsSaleConfirmedSpecification(Specification[Sale]):
    """Satisfied when a sale has been CONFIRMED for dispensing."""

    def is_satisfied_by(self, candidate: Sale) -> bool:
        return candidate.sale_status == SaleStatus.CONFIRMED


@dataclass(frozen=True, slots=True)
class IsSaleCompletedSpecification(Specification[Sale]):
    """Satisfied when a sale has been COMPLETED."""

    def is_satisfied_by(self, candidate: Sale) -> bool:
        return candidate.sale_status == SaleStatus.COMPLETED


@dataclass(frozen=True, slots=True)
class IsSaleCancelledSpecification(Specification[Sale]):
    """Satisfied when a sale is CANCELLED."""

    def is_satisfied_by(self, candidate: Sale) -> bool:
        return candidate.sale_status == SaleStatus.CANCELLED


@dataclass(frozen=True, slots=True)
class CanConfirmSaleSpecification(Specification[Sale]):
    """Satisfied when a draft sale is eligible to be confirmed."""

    def is_satisfied_by(self, candidate: Sale) -> bool:
        return candidate.sale_status == SaleStatus.DRAFT and bool(candidate.lines)


@dataclass(frozen=True, slots=True)
class CanCancelSaleSpecification(Specification[Sale]):
    """Satisfied when a sale can be cancelled."""

    def is_satisfied_by(self, candidate: Sale) -> bool:
        return candidate.sale_status not in (
            SaleStatus.COMPLETED,
            SaleStatus.CANCELLED,
            SaleStatus.RETURNED,
        )


@dataclass(frozen=True, slots=True)
class HasOutstandingPaymentSpecification(Specification[Sale]):
    """Satisfied when a sale has not been fully paid."""

    def is_satisfied_by(self, candidate: Sale) -> bool:
        return candidate.payment_status != PaymentStatus.PAID


@dataclass(frozen=True, slots=True)
class IsFullyPaidSpecification(Specification[Sale]):
    """Satisfied when a sale is fully paid."""

    def is_satisfied_by(self, candidate: Sale) -> bool:
        return candidate.payment_status == PaymentStatus.PAID


@dataclass(frozen=True, slots=True)
class HasReturnableQuantitySpecification(Specification[SaleLine]):
    """Satisfied when a sale line has returnable net quantity (> 0)."""

    def is_satisfied_by(self, candidate: SaleLine) -> bool:
        return candidate.net_quantity.is_positive() and not candidate.is_cancelled
