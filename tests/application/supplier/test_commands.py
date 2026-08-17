"""Unit tests for Supplier command DTOs."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.application.supplier import (
    ActivateSupplierCommand,
    DeactivateSupplierCommand,
    ReactivateSupplierCommand,
    RegisterSupplierCommand,
    SuspendSupplierCommand,
    UpdateSupplierAddressCommand,
    UpdateSupplierComplianceCommand,
    UpdateSupplierContactCommand,
    UpdateSupplierDetailsCommand,
)


class SupplierCommandsTests(TestCase):
    def test_register_supplier_command_instantiation(self) -> None:
        cmd = RegisterSupplierCommand(
            name="Cipla Pharma Ltd",
            phone="9876543210",
            email="info@cipla.com",
            gstin="27AAACC1206D1ZM",
            pan="AAACC1206D",
            category="MANUFACTURER",
        )
        self.assertEqual(cmd.name, "Cipla Pharma Ltd")
        self.assertEqual(cmd.gstin, "27AAACC1206D1ZM")
        self.assertEqual(cmd.category, "MANUFACTURER")

    def test_update_commands(self) -> None:
        s_id = uuid4()
        contact_cmd = UpdateSupplierContactCommand(supplier_id=s_id, phone="9111122223")
        addr_cmd = UpdateSupplierAddressCommand(
            supplier_id=s_id, street="100 Pharma Park", city="Baddi", state="Himachal Pradesh", pincode="173205"
        )
        comp_cmd = UpdateSupplierComplianceCommand(supplier_id=s_id, gstin="02AAACC1206D1Z1", pan="AAACC1206D")
        det_cmd = UpdateSupplierDetailsCommand(supplier_id=s_id, name="Cipla Distributing", category="DISTRIBUTOR")

        self.assertEqual(contact_cmd.supplier_id, s_id)
        self.assertEqual(addr_cmd.city, "Baddi")
        self.assertEqual(comp_cmd.gstin, "02AAACC1206D1Z1")
        self.assertEqual(det_cmd.category, "DISTRIBUTOR")

    def test_lifecycle_commands(self) -> None:
        s_id = uuid4()
        act_cmd = ActivateSupplierCommand(supplier_id=s_id)
        deact_cmd = DeactivateSupplierCommand(supplier_id=s_id, reason="Contract expired")
        susp_cmd = SuspendSupplierCommand(supplier_id=s_id, reason="Quality audit hold")
        react_cmd = ReactivateSupplierCommand(supplier_id=s_id, reason="Cleared audit")

        self.assertEqual(act_cmd.supplier_id, s_id)
        self.assertEqual(deact_cmd.reason, "Contract expired")
        self.assertEqual(susp_cmd.reason, "Quality audit hold")
        self.assertEqual(react_cmd.reason, "Cleared audit")
