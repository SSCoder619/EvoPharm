"""Sales application package."""
from __future__ import annotations

from .commands import (
    AddSaleLineCommand,
    AttachPrescriptionCommand,
    CancelSaleCommand,
    CompleteSaleCommand,
    ConfirmSaleCommand,
    CreateSaleCommand,
    ProcessReturnCommand,
    RecordSalePaymentCommand,
    RemoveSaleLineCommand,
)
from .exceptions import SaleNotFoundError
from .results import (
    CustomerReferenceResult,
    PrescriptionResult,
    SaleLineResult,
    SaleResult,
    SaleReturnResult,
    SaleTotalResult,
)
from .services import SalesApplicationService

__all__ = [
    "CreateSaleCommand",
    "AddSaleLineCommand",
    "RemoveSaleLineCommand",
    "AttachPrescriptionCommand",
    "ConfirmSaleCommand",
    "RecordSalePaymentCommand",
    "CompleteSaleCommand",
    "CancelSaleCommand",
    "ProcessReturnCommand",
    "SaleNotFoundError",
    "CustomerReferenceResult",
    "PrescriptionResult",
    "SaleLineResult",
    "SaleTotalResult",
    "SaleResult",
    "SaleReturnResult",
    "SalesApplicationService",
]
