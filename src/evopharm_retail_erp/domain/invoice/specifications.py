"""Specifications for the Invoice bounded context.

Reusable business predicates that evaluate an Invoice aggregate root.
They carry no mutation logic and depend purely on domain state.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from .entities import Invoice
from .enums import InvoiceStatus, PaymentStatus

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
class IsDraftInvoiceSpecification(Specification[Invoice]):
    """Satisfied when an invoice is in DRAFT status."""

    def is_satisfied_by(self, candidate: Invoice) -> bool:
        return candidate.status == InvoiceStatus.DRAFT


@dataclass(frozen=True, slots=True)
class IsIssuedInvoiceSpecification(Specification[Invoice]):
    """Satisfied when an invoice has been ISSUED."""

    def is_satisfied_by(self, candidate: Invoice) -> bool:
        return candidate.status == InvoiceStatus.ISSUED


@dataclass(frozen=True, slots=True)
class IsPaidInvoiceSpecification(Specification[Invoice]):
    """Satisfied when an invoice is fully PAID."""

    def is_satisfied_by(self, candidate: Invoice) -> bool:
        return candidate.payment_status == PaymentStatus.PAID


@dataclass(frozen=True, slots=True)
class IsPartiallyPaidInvoiceSpecification(Specification[Invoice]):
    """Satisfied when an invoice is PARTIALLY_PAID."""

    def is_satisfied_by(self, candidate: Invoice) -> bool:
        return candidate.payment_status == PaymentStatus.PARTIALLY_PAID


@dataclass(frozen=True, slots=True)
class IsCancelledInvoiceSpecification(Specification[Invoice]):
    """Satisfied when an invoice is CANCELLED."""

    def is_satisfied_by(self, candidate: Invoice) -> bool:
        return candidate.status == InvoiceStatus.CANCELLED


@dataclass(frozen=True, slots=True)
class CanIssueInvoiceSpecification(Specification[Invoice]):
    """Satisfied when a draft invoice is eligible to be issued."""

    def is_satisfied_by(self, candidate: Invoice) -> bool:
        return candidate.status == InvoiceStatus.DRAFT and bool(candidate.lines)


@dataclass(frozen=True, slots=True)
class CanCancelInvoiceSpecification(Specification[Invoice]):
    """Satisfied when an invoice can be cancelled."""

    def is_satisfied_by(self, candidate: Invoice) -> bool:
        return candidate.status not in (
            InvoiceStatus.PAID,
            InvoiceStatus.CANCELLED,
            InvoiceStatus.VOID,
        )


@dataclass(frozen=True, slots=True)
class HasOutstandingBalanceSpecification(Specification[Invoice]):
    """Satisfied when an invoice has an unpaid outstanding balance."""

    def is_satisfied_by(self, candidate: Invoice) -> bool:
        return candidate.payment_status != PaymentStatus.PAID
