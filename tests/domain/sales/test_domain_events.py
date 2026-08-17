"""Unit tests for Sales bounded context domain events."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.domain.medicine import MedicineId
from evopharm_retail_erp.domain.sales import (
    Money,
    PaymentMethod,
    PrescriptionAttached,
    PrescriptionReference,
    ReturnReason,
    Sale,
    SaleCancelled,
    SaleCompleted,
    SaleConfirmed,
    SaleCreated,
    SaleLineAdded,
    SalePaymentRecorded,
    SaleQuantity,
    SaleReturned,
    UnitPrice,
)


class SalesDomainEventsTests(TestCase):
    def test_sales_lifecycle_emits_expected_domain_events(self) -> None:
        # 1. SaleCreated
        sale = Sale.create()
        self.assertEqual(len(sale.events), 1)
        self.assertIsInstance(sale.events[0], SaleCreated)

        # 2. SaleLineAdded
        med_id = MedicineId.generate()
        line = sale.add_line(
            medicine_id=med_id,
            quantity=SaleQuantity(5),
            unit_price=UnitPrice.of("100.00"),
        )
        self.assertEqual(len(sale.events), 2)
        self.assertIsInstance(sale.events[1], SaleLineAdded)

        # 3. PrescriptionAttached
        rx = PrescriptionReference("RX-001", "Dr. Rao", "REG-888")
        sale.attach_prescription(rx)
        self.assertEqual(len(sale.events), 3)
        self.assertIsInstance(sale.events[2], PrescriptionAttached)

        # 4. SaleConfirmed
        sale.confirm()
        self.assertEqual(len(sale.events), 4)
        self.assertIsInstance(sale.events[3], SaleConfirmed)

        # 5. SalePaymentRecorded
        sale.record_payment(Money.of("500.00"), PaymentMethod.UPI)
        self.assertEqual(len(sale.events), 5)
        self.assertIsInstance(sale.events[4], SalePaymentRecorded)

        # 6. SaleCompleted
        sale.complete()
        self.assertEqual(len(sale.events), 6)
        self.assertIsInstance(sale.events[5], SaleCompleted)

        # 7. SaleReturned
        sale.process_return(line.id, SaleQuantity(2), ReturnReason.WRONG_MEDICINE)
        self.assertEqual(len(sale.events), 7)
        self.assertIsInstance(sale.events[6], SaleReturned)
