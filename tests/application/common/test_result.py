"""Unit tests for ApplicationResult container."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.application.common import ApplicationResult


class ApplicationResultTests(TestCase):
    def test_success_result_with_data(self) -> None:
        res = ApplicationResult.success({"id": 123, "status": "CONFIRMED"})

        self.assertTrue(res.is_success)
        self.assertFalse(res.is_failure)
        self.assertEqual(res.value, {"id": 123, "status": "CONFIRMED"})
        self.assertIsNone(res.error_message)
        self.assertIsNone(res.error_code)

    def test_success_result_without_data(self) -> None:
        res = ApplicationResult.success()

        self.assertTrue(res.is_success)
        self.assertIsNone(res.value)

    def test_failure_result(self) -> None:
        res = ApplicationResult.failure("Invalid operation", error_code="INVALID_STATE")

        self.assertFalse(res.is_success)
        self.assertTrue(res.is_failure)
        self.assertEqual(res.error_message, "Invalid operation")
        self.assertEqual(res.error_code, "INVALID_STATE")

        with self.assertRaises(ValueError):
            _ = res.value
