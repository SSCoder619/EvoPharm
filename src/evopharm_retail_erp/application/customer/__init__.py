"""Customer application package."""
from __future__ import annotations

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
from .results import (
    AddressResult,
    CustomerResult,
)
from .services import CustomerApplicationService

__all__ = [
    "RegisterCustomerCommand",
    "UpdateCustomerContactCommand",
    "UpdateCustomerAddressCommand",
    "UpdateCustomerProfileCommand",
    "ActivateCustomerCommand",
    "DeactivateCustomerCommand",
    "SuspendCustomerCommand",
    "CustomerNotFoundError",
    "AddressResult",
    "CustomerResult",
    "CustomerApplicationService",
]
