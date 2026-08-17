"""Unit tests for SqlAlchemyUnitOfWork implementation."""
from __future__ import annotations

from decimal import Decimal
from unittest import IsolatedAsyncioTestCase
from uuid import uuid4

from evopharm_retail_erp.domain.inventory import Inventory, Quantity
from evopharm_retail_erp.domain.medicine import (
    Composition,
    CompositionItem,
    DosageForm,
    DrugSchedule,
    GenericName,
    HSNCode,
    ManufacturerRef,
    Medicine,
    MedicineBatchId,
    MedicineId,
    MedicineName,
    PackConfiguration,
    StrengthUnit,
    UnitOfMeasure,
)
from evopharm_retail_erp.domain.purchase import (
    Purchase,
    PurchaseOrderReference,
    PurchaseQuantity,
    SupplierReference,
    UnitPrice,
)
from evopharm_retail_erp.domain.supplier import (
    GSTIN,
    PAN,
    PhoneNumber,
    Supplier,
    SupplierCode,
    SupplierName,
)
from evopharm_retail_erp.infrastructure.database.config import DatabaseSettings
from evopharm_retail_erp.infrastructure.database.session import (
    create_db_engine,
    create_session_factory,
)
from evopharm_retail_erp.infrastructure.persistence.base import Base
from evopharm_retail_erp.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


class SqlAlchemyUnitOfWorkTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.settings = DatabaseSettings(database_url="sqlite:///:memory:")
        self.engine = create_db_engine(self.settings)
        Base.metadata.create_all(self.engine)
        self.session_factory = create_session_factory(self.engine)
        self.uow = SqlAlchemyUnitOfWork(self.session_factory)

    async def asyncTearDown(self) -> None:
        self.engine.dispose()

    async def test_uow_medicine_and_inventory_transaction(self) -> None:
        m_id = MedicineId.generate()
        b_id = MedicineBatchId.generate()

        med = Medicine.register(
            name=MedicineName("Azithral 500"),
            generic_name=GenericName("Azithromycin"),
            composition=Composition.of(
                CompositionItem("Azithromycin", Decimal("500"), StrengthUnit.MG)
            ),
            manufacturer=ManufacturerRef("Alembic"),
            hsn_code=HSNCode("300490"),
            pack_configuration=PackConfiguration(5, UnitOfMeasure.TABLET),
            id=m_id,
        )

        inv = Inventory.create(
            medicine_id=m_id,
            medicine_batch_id=b_id,
            initial_quantity=Quantity(100),
        )

        async with self.uow as uow:
            uow.medicines.add(med)
            uow.inventory.add(inv)
            await uow.commit()

        async with self.uow as uow:
            res_med = uow.medicines.get_by_id(m_id)
            res_inv = uow.inventory.get_by_batch_id(b_id)

            self.assertIsNotNone(res_med)
            self.assertIsNotNone(res_inv)
            self.assertEqual(res_med.name.value, "Azithral 500")
            self.assertEqual(res_inv.quantity_on_hand.value, 100)

    async def test_uow_supplier_and_purchase_transaction(self) -> None:
        sup = Supplier.register(
            name=SupplierName("Cipla Healthcare"),
            phone=PhoneNumber("9911223344"),
            code=SupplierCode("SUP-CIPLA-01"),
            gstin=GSTIN("27ABCDE1234F1Z5"),
            pan=PAN("ABCDE1234F"),
        )
        sup_ref = SupplierReference.of(sup.id.value, code=sup.code.value, name=sup.name.value)
        po_ref = PurchaseOrderReference("PO-CIPLA-2026-01")
        purchase = Purchase.create(supplier_reference=sup_ref, order_reference=po_ref)

        async with self.uow as uow:
            uow.suppliers.add(sup)
            uow.purchases.add(purchase)
            await uow.commit()

        async with self.uow as uow:
            res_sup = uow.suppliers.get_by_id(sup.id)
            res_po = uow.purchases.get_by_order_reference(po_ref)

            self.assertIsNotNone(res_sup)
            self.assertIsNotNone(res_po)
            self.assertEqual(res_sup.code.value, "SUP-CIPLA-01")
            self.assertEqual(res_po.order_reference.value, "PO-CIPLA-2026-01")

    async def test_uow_async_context_rollback_on_exception(self) -> None:
        m_id = MedicineId.generate()
        med = Medicine.register(
            name=MedicineName("Rollback Med"),
            generic_name=GenericName("Test"),
            composition=Composition.of(
                CompositionItem("Test", Decimal("100"), StrengthUnit.MG)
            ),
            manufacturer=ManufacturerRef("Test"),
            hsn_code=HSNCode("3004"),
            pack_configuration=PackConfiguration(10, UnitOfMeasure.TABLET),
            id=m_id,
        )

        with self.assertRaises(ValueError):
            async with self.uow as uow:
                uow.medicines.add(med)
                raise ValueError("Trigger rollback")

        async with self.uow as uow:
            res = uow.medicines.get_by_id(m_id)
            self.assertIsNone(res)
