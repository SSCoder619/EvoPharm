"""Repository interfaces (ports) for the MedicineBatch domain.

These are pure contracts — no implementation, no ORM, no SQL. They
define what the MedicineBatch domain requires from persistence; concrete
adapters (SQL, in-memory, etc.) will live in the Infrastructure layer
and satisfy this Protocol structurally, with no inheritance required.
"""
from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from typing import Protocol

from ..medicine.value_objects import MedicineId
from .entities import Medicine, MedicineBatch
from .enums import BatchStatus, MedicineStatus
from .value_objects import BatchNumber, MedicineBatchId


class MedicineRepository(Protocol):
    """Persistence contract for the Medicine aggregate root."""

    def add(self, medicine: Medicine) -> None:
        """Persist a newly registered medicine master record."""
        ...

    def save(self, medicine: Medicine) -> None:
        """Persist modifications to an existing medicine master record."""
        ...

    def get_by_id(self, medicine_id: MedicineId) -> Medicine | None:
        """Retrieve a medicine master record by unique identifier."""
        ...

    def get_by_barcode(self, barcode_value: str) -> Medicine | None:
        """Retrieve a medicine master record matching a barcode value."""
        ...

    def find_by_name(
        self, query: str, *, offset: int = 0, limit: int = 20
    ) -> Sequence[Medicine]:
        """Find medicine master records by brand or alternate name."""
        ...

    def find_by_generic_name(self, generic_name: str) -> Sequence[Medicine]:
        """Find medicine master records matching a generic composition name."""
        ...

    def find_by_hsn_code(self, hsn_code: str) -> Sequence[Medicine]:
        """Find medicine master records with a matching HSN code."""
        ...

    def list_by_status(
        self, status: MedicineStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Medicine]:
        """List medicine master records matching a given status."""
        ...

    def count_by_status(self, status: MedicineStatus) -> int:
        """Count total medicine master records in a given status."""
        ...

    def exists_by_barcode(self, barcode_value: str) -> bool:
        """Check if any medicine master record has the given barcode registered."""
        ...

    def exists_by_name(self, name: str) -> bool:
        """Check if any medicine master record has the given brand name."""
        ...


class MedicineBatchRepository(Protocol):
    """Persistence contract for the MedicineBatch aggregate.

    Query methods return `Sequence[MedicineBatch]` rather than
    `list[MedicineBatch]` on purpose: callers should treat results as
    read-only data, and adapters shouldn't be forced into a specific
    concrete container just to satisfy this contract (a
    `tuple[MedicineBatch, ...]` result satisfies this Protocol exactly
    as well as a `list[MedicineBatch]` does).
    """

    def add(self, batch: MedicineBatch) -> None:
        """Persist a newly received batch."""
        ...

    def save(self, batch: MedicineBatch) -> None:
        """Persist changes to an existing batch.

        Implementations are expected to use `MedicineBatch.version` for
        optimistic-concurrency control (conditioning the write on the
        version last read) given multiple pharmacy terminals may load
        and edit the same batch concurrently.
        """
        ...

    def get_by_id(self, batch_id: MedicineBatchId) -> MedicineBatch | None:
        ...

    def get_by_batch_number(
        self, batch_number: BatchNumber
    ) -> MedicineBatch | None:
        ...

    def list_by_medicine(self, medicine_id: MedicineId) -> Sequence[MedicineBatch]:
        """All batches received for a given medicine."""
        ...

    def list_expiring_before(self, expiry_date: date) -> Sequence[MedicineBatch]:
        """Batches whose expiry date falls before the given date.

        Basis for expiry-alert and near-expiry reporting features.
        """
        ...

    def list_expired(self, reference_date: date) -> Sequence[MedicineBatch]:
        """Batches already past expiry as of the given reference date."""
        ...

    def list_available_batches(
        self, medicine_id: MedicineId
    ) -> Sequence[MedicineBatch]:
        """Batches of a medicine that currently hold sellable quantity."""
        ...

    def list_quarantined(self) -> Sequence[MedicineBatch]:
        ...

    def list_recalled(self) -> Sequence[MedicineBatch]:
        ...

    def list_by_status(
        self, status: BatchStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[MedicineBatch]:
        ...

    def count_by_status(self, status: BatchStatus) -> int:
        """Total count of batches in a given status.

        Lets the future Reports module compute dashboard totals (e.g.
        "N quarantined batches", "N recalled this quarter") without
        paging through every record via list_by_status.
        """
        ...

    def exists(self, batch_id: MedicineBatchId) -> bool:
        ...

    def exists_batch_number(self, batch_number: BatchNumber) -> bool:
        ...