"""Unit tests for Customer command DTOs."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.application.customer import (
    ActivateCustomerCommand,
    DeactivateCustomerCommand,
    RegisterCustomerCommand,
    SuspendCustomerCommand,
    UpdateCustomerAddressCommand,
    UpdateCustomerContactCommand,
    UpdateCustomerProfileCommand,
)


class CustomerCommandsTests(TestCase):
    def test_register_customer_command_instantiation(self) -> None:
        cmd = RegisterCustomerCommand(
            name="Alice Smith",
            phone="9876543210",
            email="alice@example.com",
            street="123 Main St",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001",
        )
        self.assertEqual(cmd.name, "Alice Smith")
        self.assertEqual(cmd.phone, "9876543210")
        self.assertEqual(cmd.city, "Mumbai")

    def test_update_commands(self) -> None:
        c_id = uuid4()
        contact_cmd = UpdateCustomerContactCommand(customer_id=c_id, phone="9123456789")
        addr_cmd = UpdateCustomerAddressCommand(
            customer_id=c_id, street="456 Park Ave", city="Pune", state="Maharashtra", pincode="411001"
        )
        profile_cmd = UpdateCustomerProfileCommand(customer_id=c_id, name="Alice Johnson", customer_type="VIP")

        self.assertEqual(contact_cmd.customer_id, c_id)
        self.assertEqual(addr_cmd.city, "Pune")
        self.assertEqual(profile_cmd.customer_type, "VIP")

    def test_lifecycle_commands(self) -> None:
        c_id = uuid4()
        act_cmd = ActivateCustomerCommand(customer_id=c_id)
        deact_cmd = DeactivateCustomerCommand(customer_id=c_id, reason="Moved abroad")
        susp_cmd = SuspendCustomerCommand(customer_id=c_id, reason="Billing dispute")

        self.assertEqual(act_cmd.customer_id, c_id)
        self.assertEqual(deact_cmd.reason, "Moved abroad")
        self.assertEqual(susp_cmd.reason, "Billing dispute")
