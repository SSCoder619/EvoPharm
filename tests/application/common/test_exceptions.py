"""Unit tests for Application exception hierarchy."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.application.common import (
    ApplicationError,
    ApplicationValidationError,
    ConcurrencyError,
    ConflictError,
    ForbiddenError,
    ResourceNotFoundError,
    UnauthorizedError,
)


class ApplicationExceptionsTests(TestCase):
    def test_application_error_hierarchy(self) -> None:
        err = ApplicationError("Base application error")
        self.assertEqual(err.code, "APPLICATION_ERROR")
        self.assertEqual(str(err), "Base application error")

        val_err = ApplicationValidationError("Invalid format", field="email")
        self.assertIsInstance(val_err, ApplicationError)
        self.assertEqual(val_err.field, "email")
        self.assertEqual(val_err.code, "APPLICATION_VALIDATION_ERROR")

        res_id = uuid4()
        nf_err = ResourceNotFoundError("Sale", res_id)
        self.assertIsInstance(nf_err, ApplicationError)
        self.assertIn(str(res_id), str(nf_err))
        self.assertEqual(nf_err.code, "RESOURCE_NOT_FOUND")

        c_err = ConcurrencyError("Medicine", "MED-001", expected_version=2)
        self.assertIsInstance(c_err, ConflictError)
        self.assertIsInstance(c_err, ApplicationError)
        self.assertEqual(c_err.code, "CONCURRENCY_CONFLICT")

        unauth_err = UnauthorizedError()
        self.assertEqual(unauth_err.code, "UNAUTHORIZED")

        forb_err = ForbiddenError()
        self.assertEqual(forb_err.code, "FORBIDDEN")
