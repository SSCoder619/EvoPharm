"""API Pydantic schemas package."""
from __future__ import annotations

from .customer import (
    CustomerResponse,
    RegisterCustomerRequest,
    UpdateCustomerContactRequest,
)
from .health import HealthResponse
from .inventory import (
    DispenseStockRequest,
    InventoryResponse,
    ReceiveStockRequest,
    ReleaseStockRequest,
    ReserveStockRequest,
)
from .invoice import CreateInvoiceRequest, InvoiceResponse, RecordPaymentRequest
from .medicine import MedicineResponse, RegisterMedicineRequest
from .purchase import (
    AddPurchaseLineRequest,
    CreatePurchaseRequest,
    PurchaseLineResponse,
    PurchaseResponse,
    ReceivePurchaseStockRequest,
)
from .sales import (
    AddSaleLineRequest,
    CreateSaleRequest,
    SaleLineResponse,
    SaleResponse,
)
from .supplier import (
    RegisterSupplierRequest,
    SupplierResponse,
    UpdateSupplierContactRequest,
)

__all__ = [
    "HealthResponse",
    "RegisterMedicineRequest",
    "MedicineResponse",
    "ReceiveStockRequest",
    "ReserveStockRequest",
    "ReleaseStockRequest",
    "DispenseStockRequest",
    "InventoryResponse",
    "RegisterCustomerRequest",
    "UpdateCustomerContactRequest",
    "CustomerResponse",
    "RegisterSupplierRequest",
    "UpdateSupplierContactRequest",
    "SupplierResponse",
    "CreatePurchaseRequest",
    "AddPurchaseLineRequest",
    "ReceivePurchaseStockRequest",
    "PurchaseLineResponse",
    "PurchaseResponse",
    "CreateSaleRequest",
    "AddSaleLineRequest",
    "SaleLineResponse",
    "SaleResponse",
    "CreateInvoiceRequest",
    "RecordPaymentRequest",
    "InvoiceResponse",
]
