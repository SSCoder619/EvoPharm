"""Application service for orchestrating Supplier use cases.

Translates application commands into Supplier aggregate calls, manages repository persistence,
and commits database transactions via the UnitOfWork port boundary.
"""
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from ...domain.supplier import (
    GSTIN,
    PAN,
    Address,
    EmailAddress,
    PhoneNumber,
    PostalCode,
    Supplier,
    SupplierCategory,
    SupplierCode,
    SupplierId,
    SupplierName,
)
from ..common.result import ApplicationResult
from .commands import (
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
from .exceptions import SupplierNotFoundError
from .results import SupplierResult

if TYPE_CHECKING:
    from ..common.unit_of_work import UnitOfWork


class SupplierApplicationService:
    """Orchestrates pharmaceutical supplier profile workflows across repositories and UnitOfWork boundaries."""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def register_supplier(
        self, command: RegisterSupplierCommand
    ) -> ApplicationResult[SupplierResult]:
        """Orchestrates registering a new supplier profile."""
        async with self.uow as uow:
            name = SupplierName(command.name)
            phone = PhoneNumber(command.phone)
            code = SupplierCode(command.code) if command.code else None
            email = EmailAddress(command.email) if command.email else None
            address = (
                Address(
                    street=command.street,
                    city=command.city,
                    state=command.state,
                    postal_code=PostalCode(command.pincode),
                )
                if (command.street and command.city and command.state and command.pincode)
                else None
            )
            gstin = GSTIN(command.gstin) if command.gstin else None
            pan = PAN(command.pan) if command.pan else None
            category = SupplierCategory(command.category)
            s_id = SupplierId(command.supplier_id) if command.supplier_id else None

            supplier = Supplier.register(
                name=name,
                phone=phone,
                code=code,
                email=email,
                address=address,
                gstin=gstin,
                pan=pan,
                category=category,
                id=s_id,
            )

            uow.supplier.add(supplier)
            await uow.commit()
            return ApplicationResult.success(SupplierResult.from_domain(supplier))

    async def update_contact_information(
        self, command: UpdateSupplierContactCommand
    ) -> ApplicationResult[SupplierResult]:
        """Orchestrates updating supplier phone and email contact details."""
        async with self.uow as uow:
            s_id = SupplierId(command.supplier_id)
            supplier = uow.supplier.get_by_id(s_id)
            if supplier is None:
                raise SupplierNotFoundError(command.supplier_id)

            phone = PhoneNumber(command.phone)
            email = EmailAddress(command.email) if command.email else None

            supplier.update_contact_information(phone=phone, email=email)

            uow.supplier.save(supplier)
            await uow.commit()
            return ApplicationResult.success(SupplierResult.from_domain(supplier))

    async def update_address(
        self, command: UpdateSupplierAddressCommand
    ) -> ApplicationResult[SupplierResult]:
        """Orchestrates updating supplier registered office address."""
        async with self.uow as uow:
            s_id = SupplierId(command.supplier_id)
            supplier = uow.supplier.get_by_id(s_id)
            if supplier is None:
                raise SupplierNotFoundError(command.supplier_id)

            address = Address(
                street=command.street,
                city=command.city,
                state=command.state,
                postal_code=PostalCode(command.pincode),
            )

            supplier.update_address(address)

            uow.supplier.save(supplier)
            await uow.commit()
            return ApplicationResult.success(SupplierResult.from_domain(supplier))

    async def update_compliance_information(
        self, command: UpdateSupplierComplianceCommand
    ) -> ApplicationResult[SupplierResult]:
        """Orchestrates updating supplier GSTIN and PAN tax credentials."""
        async with self.uow as uow:
            s_id = SupplierId(command.supplier_id)
            supplier = uow.supplier.get_by_id(s_id)
            if supplier is None:
                raise SupplierNotFoundError(command.supplier_id)

            gstin = GSTIN(command.gstin) if command.gstin else None
            pan = PAN(command.pan) if command.pan else None

            supplier.update_compliance_information(gstin=gstin, pan=pan)

            uow.supplier.save(supplier)
            await uow.commit()
            return ApplicationResult.success(SupplierResult.from_domain(supplier))

    async def update_supplier_details(
        self, command: UpdateSupplierDetailsCommand
    ) -> ApplicationResult[SupplierResult]:
        """Orchestrates updating supplier legal business name and category."""
        async with self.uow as uow:
            s_id = SupplierId(command.supplier_id)
            supplier = uow.supplier.get_by_id(s_id)
            if supplier is None:
                raise SupplierNotFoundError(command.supplier_id)

            name = SupplierName(command.name)
            category = SupplierCategory(command.category)

            supplier.update_supplier_details(name=name, category=category)

            uow.supplier.save(supplier)
            await uow.commit()
            return ApplicationResult.success(SupplierResult.from_domain(supplier))

    async def activate_supplier(
        self, command: ActivateSupplierCommand
    ) -> ApplicationResult[SupplierResult]:
        """Orchestrates activating an inactive supplier account."""
        async with self.uow as uow:
            s_id = SupplierId(command.supplier_id)
            supplier = uow.supplier.get_by_id(s_id)
            if supplier is None:
                raise SupplierNotFoundError(command.supplier_id)

            supplier.activate(reason=command.reason)

            uow.supplier.save(supplier)
            await uow.commit()
            return ApplicationResult.success(SupplierResult.from_domain(supplier))

    async def deactivate_supplier(
        self, command: DeactivateSupplierCommand
    ) -> ApplicationResult[SupplierResult]:
        """Orchestrates deactivating a supplier account."""
        async with self.uow as uow:
            s_id = SupplierId(command.supplier_id)
            supplier = uow.supplier.get_by_id(s_id)
            if supplier is None:
                raise SupplierNotFoundError(command.supplier_id)

            supplier.deactivate(reason=command.reason)

            uow.supplier.save(supplier)
            await uow.commit()
            return ApplicationResult.success(SupplierResult.from_domain(supplier))

    async def suspend_supplier(
        self, command: SuspendSupplierCommand
    ) -> ApplicationResult[SupplierResult]:
        """Orchestrates suspending a supplier account."""
        async with self.uow as uow:
            s_id = SupplierId(command.supplier_id)
            supplier = uow.supplier.get_by_id(s_id)
            if supplier is None:
                raise SupplierNotFoundError(command.supplier_id)

            supplier.suspend(reason=command.reason)

            uow.supplier.save(supplier)
            await uow.commit()
            return ApplicationResult.success(SupplierResult.from_domain(supplier))

    async def reactivate_supplier(
        self, command: ReactivateSupplierCommand
    ) -> ApplicationResult[SupplierResult]:
        """Orchestrates reactivating a suspended supplier account."""
        async with self.uow as uow:
            s_id = SupplierId(command.supplier_id)
            supplier = uow.supplier.get_by_id(s_id)
            if supplier is None:
                raise SupplierNotFoundError(command.supplier_id)

            supplier.reactivate(reason=command.reason)

            uow.supplier.save(supplier)
            await uow.commit()
            return ApplicationResult.success(SupplierResult.from_domain(supplier))

    async def get_supplier(
        self, supplier_id: UUID
    ) -> ApplicationResult[SupplierResult]:
        """Retrieves a supplier by ID."""
        async with self.uow as uow:
            s_id = SupplierId(supplier_id)
            supplier = uow.supplier.get_by_id(s_id)
            if supplier is None:
                raise SupplierNotFoundError(supplier_id)
            return ApplicationResult.success(SupplierResult.from_domain(supplier))
