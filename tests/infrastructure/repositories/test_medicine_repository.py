"""Unit tests for SqlAlchemyMedicineRepository using SQLite in-memory."""
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
    MedicineId,
    MedicineName,
    MedicineStatus,
    PackConfiguration,
    StrengthUnit,
    UnitOfMeasure,
)
from evopharm_retail_erp.infrastructure.database.config import DatabaseSettings
from evopharm_retail_erp.infrastructure.database.session import (
    create_db_engine,
    create_session_factory,
)
from evopharm_retail_erp.infrastructure.persistence.base import Base
from evopharm_retail_erp.infrastructure.repositories.medicine import (
    SqlAlchemyMedicineRepository,
)


class SqlAlchemyMedicineRepositoryTests(TestCase):
    def setUp(self) -> None:
        self.settings = DatabaseSettings(database_url="sqlite:///:memory:")
        self.engine = create_db_engine(self.settings)
        Base.metadata.create_all(self.engine)
        self.session_factory = create_session_factory(self.engine)
        self.session = self.session_factory()
        self.repo = SqlAlchemyMedicineRepository(self.session)

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def _sample_medicine(self, name: str = "Paracetamol 500") -> Medicine:
        return Medicine.register(
            name=MedicineName(name),
            generic_name=GenericName("Paracetamol"),
            composition=Composition.of(
                CompositionItem("Paracetamol", Decimal("500"), StrengthUnit.MG)
            ),
            manufacturer=ManufacturerRef("Cipla"),
            hsn_code=HSNCode("300490"),
            pack_configuration=PackConfiguration(10, UnitOfMeasure.TABLET),
            dosage_form=DosageForm.TABLET,
            schedule=DrugSchedule.UNSCHEDULED,
            barcodes=(Barcode("8901234560001", BarcodeType.EAN_13),),
            alternate_names=("Para 500",),
        )

    def test_add_get_by_id_and_exists(self) -> None:
        med = self._sample_medicine()
        self.repo.add(med)
        self.session.commit()

        retrieved = self.repo.get_by_id(med.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name.value, "Paracetamol 500")
        self.assertTrue(self.repo.exists_by_name("Paracetamol 500"))
        self.assertTrue(self.repo.exists_by_barcode("8901234560001"))

    def test_save_version_progression_and_concurrency_conflict(self) -> None:
        med = self._sample_medicine("Calpol 650")
        self.repo.add(med)
        self.session.commit()

        # Retrieve and mutate
        med_copy = self.repo.get_by_id(med.id)
        self.assertIsNotNone(med_copy)
        med_copy.rename(MedicineName("Calpol 650 Mg"))
        self.assertEqual(med_copy.version, 2)

        self.repo.save(med_copy)
        self.session.commit()

        updated = self.repo.get_by_id(med.id)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.name.value, "Calpol 650 Mg")
        self.assertEqual(updated.version, 2)

        # Optimistic locking error on stale save
        with self.assertRaises(ValueError):
            self.repo.save(med)  # med has version 1

    def test_queries_by_name_generic_hsn_and_status(self) -> None:
        med = self._sample_medicine("Dolo 650")
        self.repo.add(med)
        self.session.commit()

        by_name = self.repo.find_by_name("dolo")
        self.assertEqual(len(by_name), 1)

        by_generic = self.repo.find_by_generic_name("Paracetamol")
        self.assertEqual(len(by_generic), 1)

        by_hsn = self.repo.find_by_hsn_code("300490")
        self.assertEqual(len(by_hsn), 1)

        count = self.repo.count_by_status(MedicineStatus.ACTIVE)
        self.assertEqual(count, 1)
