"""Unit tests for SqlAlchemyInventoryRepository using SQLite in-memory."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.domain.inventory import (
    Inventory,
    MovementQuantity,
    Quantity,
    StockStatus,
    StockThresholds,
)
from evopharm_retail_erp.domain.medicine import MedicineBatchId, MedicineId
from evopharm_retail_erp.infrastructure.database.config import DatabaseSettings
from evopharm_retail_erp.infrastructure.database.session import (
    create_db_engine,
    create_session_factory,
)
from evopharm_retail_erp.infrastructure.persistence.base import Base
from evopharm_retail_erp.infrastructure.repositories.inventory import (
    SqlAlchemyInventoryRepository,
)


class SqlAlchemyInventoryRepositoryTests(TestCase):
    def setUp(self) -> None:
        self.settings = DatabaseSettings(database_url="sqlite:///:memory:")
        self.engine = create_db_engine(self.settings)
        Base.metadata.create_all(self.engine)
        self.session_factory = create_session_factory(self.engine)
        self.session = self.session_factory()
        self.repo = SqlAlchemyInventoryRepository(self.session)

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def test_add_get_by_id_and_exists(self) -> None:
        m_id = MedicineId.generate()
        b_id = MedicineBatchId.generate()
        inv = Inventory.create(
            medicine_id=m_id,
            medicine_batch_id=b_id,
            initial_quantity=Quantity(100),
        )

        self.repo.add(inv)
        self.session.commit()

        retrieved = self.repo.get_by_id(inv.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.quantity_on_hand.value, 100)
        self.assertTrue(self.repo.exists(inv.id))
        self.assertTrue(self.repo.exists_for_batch(b_id))

    def test_save_version_progression_and_concurrency_conflict(self) -> None:
        m_id = MedicineId.generate()
        b_id = MedicineBatchId.generate()
        inv = Inventory.create(
            medicine_id=m_id,
            medicine_batch_id=b_id,
            initial_quantity=Quantity(50),
        )
        self.repo.add(inv)
        self.session.commit()

        inv_copy = self.repo.get_by_id(inv.id)
        self.assertIsNotNone(inv_copy)
        inv_copy.record_receipt(MovementQuantity(25), reason=None)
        self.assertEqual(inv_copy.version, 2)

        self.repo.save(inv_copy)
        self.session.commit()

        updated = self.repo.get_by_id(inv.id)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.quantity_on_hand.value, 75)
        self.assertEqual(updated.version, 2)

        # Optimistic locking error on stale save
        with self.assertRaises(ValueError):
            self.repo.save(inv)  # inv has version 1

    def test_queries_by_medicine_and_status(self) -> None:
        m_id = MedicineId.generate()
        b1_id = MedicineBatchId.generate()
        b2_id = MedicineBatchId.generate()

        inv1 = Inventory.create(m_id, b1_id, Quantity(0))
        inv2 = Inventory.create(m_id, b2_id, Quantity(50))

        self.repo.add(inv1)
        self.repo.add(inv2)
        self.session.commit()

        by_med = self.repo.list_by_medicine_id(m_id)
        self.assertEqual(len(by_med), 2)

        out_of_stock = self.repo.list_out_of_stock()
        self.assertEqual(len(out_of_stock), 1)

        count = self.repo.count_by_status(StockStatus.IN_STOCK)
        self.assertEqual(count, 1)
