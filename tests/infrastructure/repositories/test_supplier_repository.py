"""Unit tests for SqlAlchemySupplierRepository using SQLite in-memory."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.domain.supplier import (
    GSTIN,
    PAN,
    Address,
    PhoneNumber,
    PostalCode,
    Supplier,
    SupplierCode,
    SupplierName,
    SupplierStatus,
)
from evopharm_retail_erp.infrastructure.database.config import DatabaseSettings
from evopharm_retail_erp.infrastructure.database.session import (
    create_db_engine,
    create_session_factory,
)
from evopharm_retail_erp.infrastructure.persistence.base import Base
from evopharm_retail_erp.infrastructure.repositories.supplier import (
    SqlAlchemySupplierRepository,
)


class SqlAlchemySupplierRepositoryTests(TestCase):
    def setUp(self) -> None:
        self.settings = DatabaseSettings(database_url="sqlite:///:memory:")
        self.engine = create_db_engine(self.settings)
        Base.metadata.create_all(self.engine)
        self.session_factory = create_session_factory(self.engine)
        self.session = self.session_factory()
        self.repo = SqlAlchemySupplierRepository(self.session)

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def _sample_supplier(self, code: str = "SUP-001") -> Supplier:
        return Supplier.register(
            name=SupplierName("Sun Pharma Distributors"),
            phone=PhoneNumber("9988776655"),
            code=SupplierCode(code),
            gstin=GSTIN("27ABCDE1234F1Z5"),
            pan=PAN("ABCDE1234F"),
        )

    def test_add_get_by_id_code_gstin_and_exists(self) -> None:
        sup = self._sample_supplier()
        self.repo.add(sup)
        self.session.commit()

        by_id = self.repo.get_by_id(sup.id)
        self.assertIsNotNone(by_id)
        self.assertEqual(by_id.name.value, "Sun Pharma Distributors")

        by_code = self.repo.get_by_code(sup.code)
        self.assertIsNotNone(by_code)

        by_gstin = self.repo.get_by_gstin(GSTIN("27ABCDE1234F1Z5"))
        self.assertIsNotNone(by_gstin)

        self.assertTrue(self.repo.exists(sup.id))
        self.assertTrue(self.repo.exists_code(sup.code))

    def test_save_version_progression_and_concurrency_conflict(self) -> None:
        sup = self._sample_supplier("SUP-002")
        self.repo.add(sup)
        self.session.commit()

        sup_copy = self.repo.get_by_id(sup.id)
        self.assertIsNotNone(sup_copy)
        sup_copy.deactivate(reason="Temporary hold")
        self.assertEqual(sup_copy.version, 2)

        self.repo.save(sup_copy)
        self.session.commit()

        updated = self.repo.get_by_id(sup.id)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.status, SupplierStatus.INACTIVE)
        self.assertEqual(updated.version, 2)

        with self.assertRaises(ValueError):
            self.repo.save(sup)  # sup is stale with version 1

    def test_list_and_count_by_status(self) -> None:
        s1 = self._sample_supplier("SUP-101")
        s2 = self._sample_supplier("SUP-102")
        self.repo.add(s1)
        self.repo.add(s2)
        self.session.commit()

        active = self.repo.list_by_status(SupplierStatus.ACTIVE)
        self.assertEqual(len(active), 2)

        count = self.repo.count_by_status(SupplierStatus.ACTIVE)
        self.assertEqual(count, 2)
