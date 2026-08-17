"""Unit tests for Supplier domain exceptions hierarchy."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.domain.supplier import (
    InvalidGSTINError,
    InvalidPANError,
    InvalidSupplierStateError,
    SupplierAlreadyActiveError,
    SupplierAlreadyInactiveError,
    SupplierDomainError,
    SupplierNotFoundError,
)


class SupplierExceptionsTests(TestCase):
    def test_exception_inheritance_and_messages(self) -> None:
        s_id = uuid4()
        err = InvalidSupplierStateError(s_id, "ACTIVE", "ACTIVE")
        self.assertIsInstance(err, SupplierDomainError)
        self.assertIn(str(s_id), str(err))

        err_inactive = SupplierAlreadyInactiveError(s_id)
        self.assertIsInstance(err_inactive, SupplierDomainError)

        err_active = SupplierAlreadyActiveError(s_id)
        self.assertIsInstance(err_active, SupplierDomainError)

        err_not_found = SupplierNotFoundError(s_id)
        self.assertIsInstance(err_not_found, SupplierDomainError)

        err_gst = InvalidGSTINError("BADGSTIN", "invalid format")
        self.assertIsInstance(err_gst, SupplierDomainError)

        err_pan = InvalidPANError("BADPAN", "invalid format")
        self.assertIsInstance(err_pan, SupplierDomainError)
