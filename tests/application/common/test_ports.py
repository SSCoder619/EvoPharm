"""Unit tests for Application ports protocol interfaces."""
from __future__ import annotations

from datetime import datetime, timezone
from unittest import IsolatedAsyncioTestCase
from uuid import UUID, uuid4

from evopharm_retail_erp.application.common import (
    ClockPort,
    EventDispatcherPort,
    IdGeneratorPort,
)


class SystemClock(ClockPort):
    def now_utc(self) -> datetime:
        return datetime.now(timezone.utc)


class RandomIdGenerator(IdGeneratorPort):
    def generate_uuid(self) -> UUID:
        return uuid4()


class MemoryEventDispatcher(EventDispatcherPort):
    def __init__(self) -> None:
        self.dispatched: list[object] = []

    async def publish(self, event: object) -> None:
        self.dispatched.append(event)

    async def publish_all(self, events: tuple[object, ...] | list[object]) -> None:
        self.dispatched.extend(events)


class ApplicationPortsTests(IsolatedAsyncioTestCase):
    def test_clock_port_implementation(self) -> None:
        clock: ClockPort = SystemClock()
        now = clock.now_utc()
        self.assertIsInstance(now, datetime)
        self.assertEqual(now.tzinfo, timezone.utc)

    def test_id_generator_port_implementation(self) -> None:
        id_gen: IdGeneratorPort = RandomIdGenerator()
        gen_id = id_gen.generate_uuid()
        self.assertIsInstance(gen_id, UUID)

    async def test_event_dispatcher_port_implementation(self) -> None:
        dispatcher: EventDispatcherPort = MemoryEventDispatcher()
        event1 = {"event": "SaleConfirmed"}
        event2 = {"event": "InvoiceIssued"}

        await dispatcher.publish(event1)
        await dispatcher.publish_all([event2])

        assert isinstance(dispatcher, MemoryEventDispatcher)
        self.assertEqual(len(dispatcher.dispatched), 2)
