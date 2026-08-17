"""Unit tests for Application UnitOfWork protocol contract."""
from __future__ import annotations

from types import TracebackType
from unittest import IsolatedAsyncioTestCase

from evopharm_retail_erp.application.common import UnitOfWork


class FakeUnitOfWork(UnitOfWork):
    """Test fake implementing UnitOfWork protocol for contract validation."""

    def __init__(self) -> None:
        self.committed: bool = False
        self.rolled_back: bool = False
        self.entered: bool = False
        self.exited: bool = False

    async def __aenter__(self) -> FakeUnitOfWork:
        self.entered = True
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.exited = True
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


class UnitOfWorkTests(IsolatedAsyncioTestCase):
    async def test_successful_commit_flow(self) -> None:
        uow = FakeUnitOfWork()

        async with uow:
            self.assertTrue(uow.entered)
            await uow.commit()

        self.assertTrue(uow.committed)
        self.assertFalse(uow.rolled_back)
        self.assertTrue(uow.exited)

    async def test_exception_triggers_rollback(self) -> None:
        uow = FakeUnitOfWork()

        with self.assertRaises(RuntimeError):
            async with uow:
                self.assertTrue(uow.entered)
                raise RuntimeError("Simulated use case failure")

        self.assertFalse(uow.committed)
        self.assertTrue(uow.rolled_back)
        self.assertTrue(uow.exited)
