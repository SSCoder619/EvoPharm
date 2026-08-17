"""API routers package."""
from __future__ import annotations

from .customer import router as customer_router
from .health import router as health_router
from .inventory import router as inventory_router
from .invoice import router as invoice_router
from .medicine import router as medicine_router
from .purchase import router as purchase_router
from .sales import router as sales_router
from .supplier import router as supplier_router

__all__ = [
    "health_router",
    "medicine_router",
    "inventory_router",
    "purchase_router",
    "sales_router",
    "customer_router",
    "supplier_router",
    "invoice_router",
]
