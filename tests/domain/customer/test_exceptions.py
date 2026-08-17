"""Unit tests for Customer domain exceptions hierarchy."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.domain.customer import (
    CustomerAlreadyActiveError,
    CustomerAlreadyInactiveError,
    CustomerDomainError,
    CustomerNotFoundError,
    InvalidCustomerStateError,
)


class CustomerExceptionsTests(TestCase):
    def test_exception_inheritance_and_messages(self) -> None:
        c_id = uuid4()
        err = InvalidCustomerStateError(c_id, "ACTIVE", "ACTIVE")
        self.assertIsInstance(err, CustomerDomainError)
        self.assertIn(str(c_id), str(err))

        err_inactive = CustomerAlreadyInactiveError(c_id)
        self.assertIsInstance(err_inactive, CustomerDomainError)

        err_active = CustomerAlreadyActiveError(c_id)
        self.assertIsInstance(err_active, CustomerDomainError)

        err_not_found = CustomerNotFoundError(c_id)
        self.assertIsInstance(err_not_found, CustomerDomainError)
