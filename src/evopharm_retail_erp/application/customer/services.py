"""Application service for orchestrating Customer use cases.

Translates application commands into Customer aggregate calls, manages repository persistence,
and commits database transactions via the UnitOfWork port boundary.
"""
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from ...domain.customer import (
    Address,
    Customer,
    CustomerCode,
    CustomerId,
    CustomerName,
    CustomerType,
    EmailAddress,
    PhoneNumber,
    PostalCode,
)
from ..common.result import ApplicationResult
from .commands import (
    ActivateCustomerCommand,
    DeactivateCustomerCommand,
    RegisterCustomerCommand,
    SuspendCustomerCommand,
    UpdateCustomerAddressCommand,
    UpdateCustomerContactCommand,
    UpdateCustomerProfileCommand,
)
from .exceptions import CustomerNotFoundError
from .results import CustomerResult

if TYPE_CHECKING:
    from ..common.unit_of_work import UnitOfWork


class CustomerApplicationService:
    """Orchestrates retail pharmacy customer profile workflows across repositories and UnitOfWork boundaries."""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def register_customer(
        self, command: RegisterCustomerCommand
    ) -> ApplicationResult[CustomerResult]:
        """Orchestrates registering a new customer profile."""
        async with self.uow as uow:
            name = CustomerName(command.name)
            phone = PhoneNumber(command.phone)
            code = CustomerCode(command.code) if command.code else None
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
            c_type = CustomerType(command.customer_type)
            c_id = CustomerId(command.customer_id) if command.customer_id else None

            customer = Customer.register(
                name=name,
                phone=phone,
                code=code,
                email=email,
                address=address,
                customer_type=c_type,
                id=c_id,
            )

            uow.customer.add(customer)
            await uow.commit()
            return ApplicationResult.success(CustomerResult.from_domain(customer))

    async def update_contact_information(
        self, command: UpdateCustomerContactCommand
    ) -> ApplicationResult[CustomerResult]:
        """Orchestrates updating customer phone and email contact details."""
        async with self.uow as uow:
            c_id = CustomerId(command.customer_id)
            customer = uow.customer.get_by_id(c_id)
            if customer is None:
                raise CustomerNotFoundError(command.customer_id)

            phone = PhoneNumber(command.phone)
            email = EmailAddress(command.email) if command.email else None

            customer.update_contact_information(phone=phone, email=email)

            uow.customer.save(customer)
            await uow.commit()
            return ApplicationResult.success(CustomerResult.from_domain(customer))

    async def update_address(
        self, command: UpdateCustomerAddressCommand
    ) -> ApplicationResult[CustomerResult]:
        """Orchestrates updating customer delivery address."""
        async with self.uow as uow:
            c_id = CustomerId(command.customer_id)
            customer = uow.customer.get_by_id(c_id)
            if customer is None:
                raise CustomerNotFoundError(command.customer_id)

            address = Address(
                street=command.street,
                city=command.city,
                state=command.state,
                postal_code=PostalCode(command.pincode),
            )

            customer.update_address(address)

            uow.customer.save(customer)
            await uow.commit()
            return ApplicationResult.success(CustomerResult.from_domain(customer))

    async def update_profile(
        self, command: UpdateCustomerProfileCommand
    ) -> ApplicationResult[CustomerResult]:
        """Orchestrates updating customer name and classification."""
        async with self.uow as uow:
            c_id = CustomerId(command.customer_id)
            customer = uow.customer.get_by_id(c_id)
            if customer is None:
                raise CustomerNotFoundError(command.customer_id)

            name = CustomerName(command.name)
            c_type = CustomerType(command.customer_type)

            customer.update_profile(name=name, customer_type=c_type)

            uow.customer.save(customer)
            await uow.commit()
            return ApplicationResult.success(CustomerResult.from_domain(customer))

    async def activate_customer(
        self, command: ActivateCustomerCommand
    ) -> ApplicationResult[CustomerResult]:
        """Orchestrates activating a customer account."""
        async with self.uow as uow:
            c_id = CustomerId(command.customer_id)
            customer = uow.customer.get_by_id(c_id)
            if customer is None:
                raise CustomerNotFoundError(command.customer_id)

            customer.activate(reason=command.reason)

            uow.customer.save(customer)
            await uow.commit()
            return ApplicationResult.success(CustomerResult.from_domain(customer))

    async def deactivate_customer(
        self, command: DeactivateCustomerCommand
    ) -> ApplicationResult[CustomerResult]:
        """Orchestrates deactivating a customer account."""
        async with self.uow as uow:
            c_id = CustomerId(command.customer_id)
            customer = uow.customer.get_by_id(c_id)
            if customer is None:
                raise CustomerNotFoundError(command.customer_id)

            customer.deactivate(reason=command.reason)

            uow.customer.save(customer)
            await uow.commit()
            return ApplicationResult.success(CustomerResult.from_domain(customer))

    async def suspend_customer(
        self, command: SuspendCustomerCommand
    ) -> ApplicationResult[CustomerResult]:
        """Orchestrates suspending a customer account."""
        async with self.uow as uow:
            c_id = CustomerId(command.customer_id)
            customer = uow.customer.get_by_id(c_id)
            if customer is None:
                raise CustomerNotFoundError(command.customer_id)

            customer.suspend(reason=command.reason)

            uow.customer.save(customer)
            await uow.commit()
            return ApplicationResult.success(CustomerResult.from_domain(customer))

    async def get_customer(
        self, customer_id: UUID
    ) -> ApplicationResult[CustomerResult]:
        """Retrieves a customer by ID."""
        async with self.uow as uow:
            c_id = CustomerId(customer_id)
            customer = uow.customer.get_by_id(c_id)
            if customer is None:
                raise CustomerNotFoundError(customer_id)
            return ApplicationResult.success(CustomerResult.from_domain(customer))
