"""Specifications for the Inventory bounded context.

Reusable business predicates that evaluate an Inventory aggregate projection.
They carry no mutation logic and depend purely on domain state.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from .entities import Inventory
from .enums import StockStatus
from .value_objects import Quantity

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
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(
            candidate
        )


@dataclass(frozen=True, slots=True)
class OrSpecification(Specification[CandidateT]):
    left: Specification[CandidateT]
    right: Specification[CandidateT]

    def is_satisfied_by(self, candidate: CandidateT) -> bool:
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(
            candidate
        )


@dataclass(frozen=True, slots=True)
class NotSpecification(Specification[CandidateT]):
    spec: Specification[CandidateT]

    def is_satisfied_by(self, candidate: CandidateT) -> bool:
        return not self.spec.is_satisfied_by(candidate)


@dataclass(frozen=True, slots=True)
class IsLowStockSpecification(Specification[Inventory]):
    """Satisfied when an inventory item's stock is at or below reorder level."""

    def is_satisfied_by(self, candidate: Inventory) -> bool:
        return candidate.status == StockStatus.LOW_STOCK


@dataclass(frozen=True, slots=True)
class IsOutOfStockSpecification(Specification[Inventory]):
    """Satisfied when an inventory item has zero available quantity."""

    def is_satisfied_by(self, candidate: Inventory) -> bool:
        return candidate.status == StockStatus.OUT_OF_STOCK


@dataclass(frozen=True, slots=True)
class IsOverstockedSpecification(Specification[Inventory]):
    """Satisfied when an inventory item's stock exceeds overstock level."""

    def is_satisfied_by(self, candidate: Inventory) -> bool:
        return candidate.status == StockStatus.OVERSTOCKED


@dataclass(frozen=True, slots=True)
class HasAvailableStockSpecification(Specification[Inventory]):
    """Satisfied when an inventory item has positive available stock (> 0)."""

    def is_satisfied_by(self, candidate: Inventory) -> bool:
        return candidate.quantity_available.is_positive()


@dataclass(frozen=True, slots=True)
class HasReservedStockSpecification(Specification[Inventory]):
    """Satisfied when an inventory item currently has reserved quantity (> 0)."""

    def is_satisfied_by(self, candidate: Inventory) -> bool:
        return candidate.quantity_reserved.is_positive()


@dataclass(frozen=True, slots=True)
class IsStockSufficientSpecification(Specification[Inventory]):
    """Satisfied when an inventory item has at least the required quantity available."""

    required_quantity: Quantity

    def is_satisfied_by(self, candidate: Inventory) -> bool:
        return candidate.quantity_available >= self.required_quantity


@dataclass(frozen=True, slots=True)
class NeedsReorderSpecification(IsLowStockSpecification):
    """Satisfied when an inventory item needs reorder replenishment."""


@dataclass(frozen=True, slots=True)
class OverstockSpecification(IsOverstockedSpecification):
    """Satisfied when an inventory item is in an overstocked condition."""


@dataclass(frozen=True, slots=True)
class CanReserveStockSpecification(IsStockSufficientSpecification):
    """Satisfied when an inventory item can reserve the requested quantity."""
