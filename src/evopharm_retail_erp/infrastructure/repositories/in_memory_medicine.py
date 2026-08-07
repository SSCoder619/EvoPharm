"""In-memory MedicineRepository adapter.

This adapter is useful for local composition and application-service tests.
It is intentionally an infrastructure implementation of the domain port,
not a second domain model or a shortcut around the application layer.
"""
from __future__ import annotations

from copy import deepcopy
from collections.abc import Sequence

from evopharm_retail_erp.domain.medicine import (
    Medicine,
    MedicineId,
    MedicineRepository,
    MedicineStatus,
)


class InMemoryMedicineRepository(MedicineRepository):
    """A defensive-copy repository with basic catalogue lookup semantics."""

    def __init__(self) -> None:
        self._medicines: dict[MedicineId, Medicine] = {}

    def add(self, medicine: Medicine) -> None:
        if medicine.id in self._medicines:
            raise ValueError(f"Medicine {medicine.id} already exists")
        if self.exists_by_barcode_for_other(medicine):
            raise ValueError("A medicine with one of these barcodes already exists")
        self._medicines[medicine.id] = deepcopy(medicine)

    def save(self, medicine: Medicine) -> None:
        persisted = self._medicines.get(medicine.id)
        if persisted is None:
            raise KeyError(f"Medicine {medicine.id} does not exist")
        if medicine.version != persisted.version + 1:
            raise ValueError(
                "Stale or invalid Medicine version; expected exactly one domain mutation"
            )
        if self.exists_by_barcode_for_other(medicine):
            raise ValueError("A medicine with one of these barcodes already exists")
        self._medicines[medicine.id] = deepcopy(medicine)

    def get_by_id(self, medicine_id: MedicineId) -> Medicine | None:
        medicine = self._medicines.get(medicine_id)
        return deepcopy(medicine) if medicine is not None else None

    def get_by_barcode(self, barcode_value: str) -> Medicine | None:
        for medicine in self._medicines.values():
            if medicine.has_barcode(barcode_value):
                return deepcopy(medicine)
        return None

    def find_by_name(
        self, query: str, *, offset: int = 0, limit: int = 20
    ) -> Sequence[Medicine]:
        if offset < 0 or limit < 0:
            raise ValueError("offset and limit must not be negative")
        normalized_query = " ".join(query.split()).casefold()
        matches = [
            medicine
            for medicine in self._medicines.values()
            if normalized_query in medicine.name.value.casefold()
            or any(
                normalized_query in alternate_name.casefold()
                for alternate_name in medicine.alternate_names
            )
        ]
        matches.sort(key=lambda medicine: medicine.name.value.casefold())
        return tuple(deepcopy(medicine) for medicine in matches[offset : offset + limit])

    def find_by_generic_name(self, generic_name: str) -> Sequence[Medicine]:
        normalized_name = " ".join(generic_name.split()).casefold()
        return tuple(
            deepcopy(medicine)
            for medicine in self._medicines.values()
            if medicine.generic_name.value.casefold() == normalized_name
        )

    def find_by_hsn_code(self, hsn_code: str) -> Sequence[Medicine]:
        return tuple(
            deepcopy(medicine)
            for medicine in self._medicines.values()
            if medicine.hsn_code.value == hsn_code.strip()
        )

    def list_by_status(
        self, status: MedicineStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Medicine]:
        if offset < 0 or limit < 0:
            raise ValueError("offset and limit must not be negative")
        medicines = [
            medicine for medicine in self._medicines.values() if medicine.status is status
        ]
        medicines.sort(key=lambda medicine: medicine.name.value.casefold())
        return tuple(deepcopy(medicine) for medicine in medicines[offset : offset + limit])

    def count_by_status(self, status: MedicineStatus) -> int:
        return sum(
            medicine.status is status for medicine in self._medicines.values()
        )

    def exists_by_barcode(self, barcode_value: str) -> bool:
        return self.get_by_barcode(barcode_value) is not None

    def exists_by_name(self, name: str) -> bool:
        normalized_name = " ".join(name.split()).casefold()
        return any(
            medicine.name.value.casefold() == normalized_name
            for medicine in self._medicines.values()
        )

    def exists_by_barcode_for_other(self, candidate: Medicine) -> bool:
        candidate_barcodes = {barcode.value for barcode in candidate.barcodes}
        return any(
            medicine.id != candidate.id
            and any(barcode.value in candidate_barcodes for barcode in medicine.barcodes)
            for medicine in self._medicines.values()
        )
