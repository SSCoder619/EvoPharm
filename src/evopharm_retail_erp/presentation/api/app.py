"""FastAPI application factory for EvoPharm Retail ERP."""
from __future__ import annotations

from fastapi import FastAPI
from .exception_handlers import register_exception_handlers
from .routers import (
    customer_router,
    health_router,
    inventory_router,
    invoice_router,
    medicine_router,
    purchase_router,
    sales_router,
    supplier_router,
)


def create_app() -> FastAPI:
    """Application factory producing a configured FastAPI application instance."""
    app = FastAPI(
        title="EvoPharm Retail ERP API",
        version="1.0.0",
        description="RESTful Backend API for EvoPharm Retail ERP Framework",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    register_exception_handlers(app)

    # Register bounded context routers
    app.include_router(health_router)
    app.include_router(medicine_router)
    app.include_router(inventory_router)
    app.include_router(purchase_router)
    app.include_router(sales_router)
    app.include_router(customer_router)
    app.include_router(supplier_router)
    app.include_router(invoice_router)

    return app


app = create_app()
