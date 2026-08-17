"""Bidirectional mapping functions between Medicine domain aggregate and ORM models."""
from __future__ import annotations

import json
from decimal import Decimal

from evopharm_retail_erp.domain.medicine import (
    Barcode,
    BarcodeType,
    BatchNumber,
    BatchQuantity,
    BatchSource,
    BatchStatus,
    Composition,
    CompositionItem,
    DosageForm,
    DrugSchedule,
    ExpiryDate,
    GenericName,
    HSNCode,
    ManufacturerRef,
    ManufacturingDate,
    Medicine,
    MedicineBatch,
    MedicineBatchId,
    MedicineId,
    MedicineName,
    MedicineStatus,
    PackConfiguration,
    QuarantineReason,
    ReceivedDate,
    StockAdjustmentReason,
    StorageCondition,
    StrengthUnit,
    UnitOfMeasure,
)
from ..models.medicine import (
    MedicineAlternateNameORM,
    MedicineBarcodeORM,
    MedicineBatchORM,
    MedicineORM,
)


def medicine_to_orm(medicine: Medicine) -> MedicineORM:
    """Convert a Medicine aggregate root into a MedicineORM model."""
    comp_data = [
        {
            "ingredient": item.ingredient,
            "strength": str(item.strength),
            "unit": item.unit.value,
        }
        for item in medicine.composition.items
    ]

    sc = medicine.storage_condition
    orm = MedicineORM(
        id=medicine.id.value,
        name=medicine.name.value,
        generic_name=medicine.generic_name.value,
        composition_json=json.dumps(comp_data),
        manufacturer=medicine.manufacturer.name,
        hsn_code=medicine.hsn_code.value,
        pack_size=medicine.pack_configuration.units_per_pack,
        unit_of_measure=medicine.pack_configuration.unit_of_measure.value,
        dosage_form=medicine.dosage_form.value,
        schedule=medicine.schedule.value,
        status=medicine.status.value,
        storage_description=sc.description if sc else None,
        created_at=medicine.created_at,
        updated_at=medicine.updated_at,
        version=medicine.version,
    )

    orm.barcodes = [
        MedicineBarcodeORM(
            medicine_id=medicine.id.value,
            barcode_value=bc.value,
            barcode_type=bc.barcode_type.value,
        )
        for bc in medicine.barcodes
    ]

    orm.alternate_names = [
        MedicineAlternateNameORM(
            medicine_id=medicine.id.value,
            name=name,
        )
        for name in medicine.alternate_names
    ]

    orm.batches = [
        MedicineBatchORM(
            id=b.id.value,
            medicine_id=medicine.id.value,
            batch_number=b.batch_number.value,
            manufacturing_date=b.manufacturing_date.value,
            expiry_date=b.expiry_date.value,
            received_date=b.received_date.value,
            quantity=b.quantity.value,
            source=b.source.value,
            status=b.status.value,
            quarantine_reason=b.quarantine_reason.value if b.quarantine_reason else None,
            adjustment_reason=b.adjustment_reason.value if b.adjustment_reason else None,
            recall_note=b.recall_note,
            created_at=b.created_at,
            updated_at=b.updated_at,
        )
        for b in medicine.batches
    ]

    return orm


def orm_to_medicine(orm: MedicineORM) -> Medicine:
    """Reconstruct a Medicine aggregate root from a MedicineORM model."""
    comp_list = json.loads(orm.composition_json)
    comp_items = [
        CompositionItem(
            ingredient=item["ingredient"],
            strength=Decimal(str(item["strength"])),
            unit=StrengthUnit(item["unit"]),
        )
        for item in comp_list
    ]
    composition = Composition.of(*comp_items)

    storage_cond = (
        StorageCondition(description=orm.storage_description)
        if orm.storage_description
        else None
    )

    barcodes = [
        Barcode(
            value=bc.barcode_value,
            barcode_type=BarcodeType(bc.barcode_type),
        )
        for bc in orm.barcodes
    ]

    clean_alternates = [alt.name for alt in orm.alternate_names]

    medicine = Medicine(
        id=MedicineId(orm.id),
        name=MedicineName(orm.name),
        generic_name=GenericName(orm.generic_name),
        composition=composition,
        manufacturer=ManufacturerRef(orm.manufacturer),
        hsn_code=HSNCode(orm.hsn_code),
        pack_configuration=PackConfiguration(
            units_per_pack=orm.pack_size,
            unit_of_measure=UnitOfMeasure(orm.unit_of_measure),
        ),
        dosage_form=DosageForm(orm.dosage_form),
        schedule=DrugSchedule(orm.schedule),
        status=MedicineStatus(orm.status),
        storage_condition=storage_cond,
        _barcodes=set(barcodes),
        _alternate_names=clean_alternates,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
        version=orm.version,
    )

    batches_dict: dict[str, MedicineBatch] = {}
    for b_orm in orm.batches:
        batch = MedicineBatch(
            id=MedicineBatchId(b_orm.id),
            batch_number=BatchNumber(b_orm.batch_number),
            manufacturing_date=ManufacturingDate(b_orm.manufacturing_date),
            expiry_date=ExpiryDate(b_orm.expiry_date),
            received_date=ReceivedDate(b_orm.received_date),
            quantity=BatchQuantity(b_orm.quantity),
            source=BatchSource(b_orm.source),
            status=BatchStatus(b_orm.status),
            quarantine_reason=QuarantineReason(b_orm.quarantine_reason) if b_orm.quarantine_reason else None,
            adjustment_reason=StockAdjustmentReason(b_orm.adjustment_reason) if b_orm.adjustment_reason else None,
            recall_note=b_orm.recall_note,
            created_at=b_orm.created_at,
            updated_at=b_orm.updated_at,
        )
        batches_dict[batch.batch_number.value] = batch

    object.__setattr__(medicine, "_batches", batches_dict)
    return medicine
