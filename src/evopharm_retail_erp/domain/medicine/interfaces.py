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
from .entities import MedicineBatch
from .enums import BatchStatus
from .value_objects import BatchNumber, MedicineBatchId


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