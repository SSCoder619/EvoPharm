"""Unit tests for Supplier domain events."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.domain.supplier import (
    GSTIN,
    PAN,
    Address,
    EmailAddress,
    PhoneNumber,
    PostalCode,
    Supplier,
    SupplierActivated,
    SupplierAddressUpdated,
    SupplierCategory,
    SupplierComplianceUpdated,
    SupplierContactUpdated,
    SupplierDeactivated,
    SupplierDetailsUpdated,
    SupplierName,
    SupplierReactivated,
    SupplierRegistered,
    SupplierSuspended,
)


class SupplierDomainEventsTests(TestCase):
    def test_supplier_events_emission(self) -> None:
        # 1. SupplierRegistered
        supplier = Supplier.register(
            name=SupplierName("HealthCorp Logistics"),
            phone=PhoneNumber("+919000000001"),
        )
        self.assertEqual(len(supplier.events), 1)
        self.assertIsInstance(supplier.events[0], SupplierRegistered)

        # 2. SupplierContactUpdated
        new_phone = PhoneNumber("+919000000002")
        supplier.update_contact_information(new_phone, EmailAddress("health@example.com"))
        self.assertEqual(len(supplier.events), 2)
        self.assertIsInstance(supplier.events[1], SupplierContactUpdated)

        # 3. SupplierAddressUpdated
        addr = Address("123 Logistics Way", "Chennai", "Tamil Nadu", PostalCode("600001"))
        supplier.update_address(addr)
        self.assertEqual(len(supplier.events), 3)
        self.assertIsInstance(supplier.events[2], SupplierAddressUpdated)

        # 4. SupplierComplianceUpdated
        supplier.update_compliance_information(GSTIN("29ABCDE1234F1Z5"), PAN("ABCDE1234F"))
        self.assertEqual(len(supplier.events), 4)
        self.assertIsInstance(supplier.events[3], SupplierComplianceUpdated)

        # 5. SupplierDetailsUpdated
        supplier.update_supplier_details(SupplierName("HealthCorp Global"), SupplierCategory.MANUFACTURER)
        self.assertEqual(len(supplier.events), 5)
        self.assertIsInstance(supplier.events[4], SupplierDetailsUpdated)

        # 6. SupplierDeactivated & SupplierActivated
        supplier.deactivate("Temporary contract hold")
        self.assertIsInstance(supplier.events[5], SupplierDeactivated)

        supplier.activate()
        self.assertIsInstance(supplier.events[6], SupplierActivated)

        # 7. SupplierSuspended & SupplierReactivated
        supplier.suspend("Quality issue")
        self.assertIsInstance(supplier.events[7], SupplierSuspended)

        supplier.reactivate("Quality cleared")
        self.assertIsInstance(supplier.events[8], SupplierReactivated)
