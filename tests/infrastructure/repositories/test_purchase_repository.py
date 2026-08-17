"""Unit tests for SqlAlchemyPurchaseRepository using SQLite in-memory."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.domain.medicine import MedicineId
from evopharm_retail_erp.domain.purchase import (
    InvoiceReference,
    Purchase,
    PurchaseOrderReference,
    PurchaseQuantity,
    PurchaseStatus,
    ReceivingStatus,
    SupplierReference,
    UnitPrice,
)
from evopharm_retail_erp.infrastructure.database.config import DatabaseSettings
from evopharm_retail_erp.infrastructure.database.session import (
    create_db_engine,
    create_session_factory,
)
from evopharm_retail_erp.infrastructure.persistence.base import Base
from evopharm_retail_erp.infrastructure.repositories.purchase import (
    SqlAlchemyPurchaseRepository,
)


class SqlAlchemyPurchaseRepositoryTests(TestCase):
    def setUp(self) -> None:
        self.settings = DatabaseSettings(database_url="sqlite:///:memory:")
        self.engine = create_db_engine(self.settings)
        Base.metadata.create_all(self.engine)
        self.session_factory = create_session_factory(self.engine)
        self.session = self.session_factory()
        self.repo = SqlAlchemyPurchaseRepository(self.session)

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def test_add_get_by_id_order_ref_invoice_ref_and_exists(self) -> None:
        sup_id = uuid4()
        sup_ref = SupplierReference.of(sup_id, code="SUP-01", name="Apex")
        po_ref = PurchaseOrderReference("PO-2026-100")
        inv_ref = InvoiceReference("INV-2026-100")

        purchase = Purchase.create(sup_ref, po_ref, inv_ref)
        m_id = MedicineId.generate()
        purchase.add_line(m_id, PurchaseQuantity(10), UnitPrice.of("50.00"))

        self.repo.add(purchase)
        self.session.commit()

        by_id = self.repo.get_by_id(purchase.id)
        self.assertIsNotNone(by_id)
        self.assertEqual(len(by_id.lines), 1)

        by_po = self.repo.get_by_order_reference(po_ref)
        self.assertIsNotNone(by_po)

        by_inv = self.repo.get_by_invoice_reference(inv_ref)
        self.assertIsNotNone(by_inv)

        self.assertTrue(self.repo.exists(purchase.id))
        self.assertTrue(self.repo.exists_order_reference(po_ref))

    def test_save_version_progression_and_concurrency_conflict(self) -> None:
        sup_ref = SupplierReference.of(uuid4(), code="SUP-02", name="Beta")
        po_ref = PurchaseOrderReference("PO-2026-200")
        purchase = Purchase.create(sup_ref, po_ref)
        m_id = MedicineId.generate()
        purchase.add_line(m_id, PurchaseQuantity(20), UnitPrice.of("25.00"))

        self.repo.add(purchase)
        self.session.commit()

        p_copy = self.repo.get_by_id(purchase.id)
        self.assertIsNotNone(p_copy)
        p_copy.approve()
        self.assertEqual(p_copy.version, 3)  # add_line touched (v2), approve touched (v3)

        self.repo.save(p_copy)
        self.session.commit()

        updated = self.repo.get_by_id(purchase.id)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.purchase_status, PurchaseStatus.APPROVED)

        with self.assertRaises(ValueError):
            self.repo.save(purchase)  # purchase is stale

    def test_list_by_supplier_and_status(self) -> None:
        sup_id = uuid4()
        sup_ref = SupplierReference.of(sup_id, code="SUP-03", name="Gamma")
        p1 = Purchase.create(sup_ref, PurchaseOrderReference("PO-301"))
        p2 = Purchase.create(sup_ref, PurchaseOrderReference("PO-302"))

        self.repo.add(p1)
        self.repo.add(p2)
        self.session.commit()

        by_sup = self.repo.list_by_supplier(sup_id)
        self.assertEqual(len(by_sup), 2)

        by_status = self.repo.list_by_status(PurchaseStatus.DRAFT)
        self.assertEqual(len(by_status), 2)

        count = self.repo.count_by_status(PurchaseStatus.DRAFT)
        self.assertEqual(count, 2)
