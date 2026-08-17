"""Unit tests for Medicine aggregate <-> ORM mapping."""
from __future__ import annotations

from decimal import Decimal
from unittest import TestCase

from evopharm_retail_erp.domain.medicine import (
    Barcode,
    BarcodeType,
    Composition,
    CompositionItem,
    DosageForm,
    DrugSchedule,
    GenericName,
    HSNCode,
    ManufacturerRef,
    Medicine,
    MedicineName,
    PackConfiguration,
    StrengthUnit,
    UnitOfMeasure,
)
from evopharm_retail_erp.infrastructure.persistence.mappers.medicine_mapper import (
    medicine_to_orm,
    orm_to_medicine,
)


class MedicineMappingTests(TestCase):
    def test_roundtrip_medicine_mapping(self) -> None:
        med = Medicine.register(
            name=MedicineName("Crocin 500"),
            generic_name=GenericName("Paracetamol"),
            composition=Composition.of(
                CompositionItem("Paracetamol", Decimal("500"), StrengthUnit.MG)
            ),
            manufacturer=ManufacturerRef("GSK"),
            hsn_code=HSNCode("300490"),
            pack_configuration=PackConfiguration(15, UnitOfMeasure.TABLET),
            dosage_form=DosageForm.TABLET,
            schedule=DrugSchedule.UNSCHEDULED,
            barcodes=(Barcode("8901234567890", BarcodeType.EAN_13),),
            alternate_names=("Crocin tablet",),
        )

        orm = medicine_to_orm(med)
        self.assertEqual(orm.name, "Crocin 500")
        self.assertEqual(orm.generic_name, "Paracetamol")
        self.assertEqual(len(orm.barcodes), 1)

        reconstructed = orm_to_medicine(orm)
        self.assertEqual(reconstructed.id, med.id)
        self.assertEqual(reconstructed.name.value, "Crocin 500")
        self.assertEqual(reconstructed.generic_name.value, "Paracetamol")
        self.assertEqual(reconstructed.alternate_names, ("Crocin tablet",))
        self.assertTrue(reconstructed.has_barcode("8901234567890"))
