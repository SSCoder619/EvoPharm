"""Executable boundary tests for the Medicine Catalogue vertical slice."""
from __future__ import annotations

import json
from decimal import Decimal
from tempfile import TemporaryDirectory
from unittest import TestCase
from pathlib import Path

from evopharm_retail_erp.application.medicine import (
    RegisterMedicineCommand,
    RegisterMedicineService,
)
from evopharm_retail_erp.domain.medicine import (
    Barcode,
    BarcodeType,
    Composition,
    CompositionItem,
    DosageForm,
    GenericName,
    HSNCode,
    InvalidHSNCodeError,
    ManufacturerRef,
    MedicineName,
    MedicineStatus,
    PackConfiguration,
    StrengthUnit,
    UnitOfMeasure,
)
from evopharm_retail_erp.infrastructure.logging import FileAuditLogger
from evopharm_retail_erp.infrastructure.repositories import InMemoryMedicineRepository


class MedicineCatalogueArchitectureTests(TestCase):
    def setUp(self) -> None:
        self.repository = InMemoryMedicineRepository()
        self.service = RegisterMedicineService(self.repository)

    def _command(self, *, name: str = "Calpol 500", alternate_names: tuple[str, ...] = ()) -> RegisterMedicineCommand:
        return RegisterMedicineCommand(
            name=MedicineName(name),
            generic_name=GenericName("Paracetamol"),
            composition=Composition.of(
                CompositionItem("Paracetamol", Decimal("500"), StrengthUnit.MG)
            ),
            manufacturer=ManufacturerRef("Mediwell Laboratories"),
            dosage_form=DosageForm.TABLET,
            pack_configuration=PackConfiguration(10, UnitOfMeasure.TABLET),
            hsn_code=HSNCode("3004"),
            barcodes=(Barcode("8901234567890", BarcodeType.EAN_13),),
            alternate_names=alternate_names,
        )

    def test_application_service_coordinates_domain_and_repository_port(self) -> None:
        registered = self.service.execute(
            self._command(alternate_names=("Calpol tablet", "CALPOL TABLET"))
        )

        persisted = self.repository.get_by_id(registered.id)

        self.assertIsNotNone(persisted)
        assert persisted is not None
        self.assertEqual(persisted, registered)
        self.assertIsNot(persisted, registered)
        self.assertEqual(persisted.alternate_names, ("Calpol tablet",))
        self.assertTrue(self.repository.exists_by_barcode("8901234567890"))
        self.assertTrue(self.repository.exists_by_name("  calpol 500 "))

    def test_repository_returns_defensive_copy_and_enforces_version_progression(self) -> None:
        registered = self.service.execute(self._command())
        editable_copy = self.repository.get_by_id(registered.id)
        assert editable_copy is not None

        editable_copy.rename(MedicineName("Calpol 650"))
        self.repository.save(editable_copy)

        current = self.repository.get_by_id(registered.id)
        assert current is not None
        self.assertEqual(current.name.value, "Calpol 650")
        self.assertEqual(current.version, 2)
        with self.assertRaises(ValueError):
            self.repository.save(registered)

    def test_catalogue_search_and_lifecycle_queries_are_adapter_concerns(self) -> None:
        registered = self.service.execute(
            self._command(alternate_names=("Acetaminophen 500",))
        )
        editable_copy = self.repository.get_by_id(registered.id)
        assert editable_copy is not None
        editable_copy.mark_under_review("Packaging update")
        self.repository.save(editable_copy)

        self.assertEqual(
            [medicine.id for medicine in self.repository.find_by_name("acetaminophen")],
            [registered.id],
        )
        self.assertEqual(
            self.repository.count_by_status(MedicineStatus.UNDER_REVIEW), 1
        )

    def test_value_objects_reject_invalid_regulatory_data_before_persistence(self) -> None:
        with self.assertRaises(InvalidHSNCodeError):
            HSNCode("30A4")

    def test_file_audit_logger_is_an_infrastructure_adapter(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            audit_path = Path(temporary_directory) / "audit" / "events.jsonl"
            FileAuditLogger(audit_path).log_event(
                user_id="operator-1",
                action="MEDICINE_REGISTERED",
                details="medicine master created",
            )

            self.assertTrue(audit_path.exists())
            record = json.loads(audit_path.read_text(encoding="utf-8"))
            self.assertEqual(record["action"], "MEDICINE_REGISTERED")
            self.assertEqual(record["user_id"], "operator-1")
