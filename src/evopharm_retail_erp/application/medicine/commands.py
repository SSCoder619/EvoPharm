"""Immutable input models for Medicine Catalogue use cases."""
from __future__ import annotations

from dataclasses import dataclass, field

from evopharm_retail_erp.domain.medicine import (
    Barcode,
    Composition,
    DosageForm,
    DrugSchedule,
    GenericName,
    HSNCode,
    ManufacturerRef,
    MedicineName,
    PackConfiguration,
    StorageCondition,
)


@dataclass(frozen=True, slots=True)
class RegisterMedicineCommand:
    """Validated information required to register a medicine master record.

    UI and API adapters construct domain value objects before invoking this
    command.  This keeps parsing and transport concerns at the outer edge,
    while the application layer simply coordinates one domain use case.
    """

    name: MedicineName
    generic_name: GenericName
    composition: Composition
    manufacturer: ManufacturerRef
    dosage_form: DosageForm
    pack_configuration: PackConfiguration
    hsn_code: HSNCode
    schedule: DrugSchedule = DrugSchedule.UNSCHEDULED
    barcodes: tuple[Barcode, ...] = field(default_factory=tuple)
    alternate_names: tuple[str, ...] = field(default_factory=tuple)
    storage_condition: StorageCondition | None = None
