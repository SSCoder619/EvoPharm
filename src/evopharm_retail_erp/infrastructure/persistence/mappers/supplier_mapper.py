"""Bidirectional mapping functions between Supplier domain aggregate and ORM models."""
from __future__ import annotations

from evopharm_retail_erp.domain.supplier import (
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
    SupplierStatus,
)
from ..models.supplier import SupplierORM


def supplier_to_orm(supplier: Supplier) -> SupplierORM:
    """Convert a Supplier aggregate root into a SupplierORM model."""
    addr = supplier.address
    return SupplierORM(
        id=supplier.id.value,
        code=supplier.code.value,
        name=supplier.name.value,
        phone=supplier.phone.value,
        email=supplier.email.value if supplier.email else None,
        street=addr.street if addr else None,
        city=addr.city if addr else None,
        state=addr.state if addr else None,
        postal_code=addr.postal_code.value if addr else None,
        country=addr.country if addr else None,
        gstin=supplier.gstin.value if supplier.gstin else None,
        pan=supplier.pan.value if supplier.pan else None,
        status=supplier.status.value,
        category=supplier.category.value,
        created_at=supplier.created_at,
        updated_at=supplier.updated_at,
        version=supplier.version,
    )


def orm_to_supplier(orm: SupplierORM) -> Supplier:
    """Reconstruct a Supplier aggregate root from a SupplierORM model."""
    address = None
    if orm.street and orm.city and orm.state and orm.postal_code:
        address = Address(
            street=orm.street,
            city=orm.city,
            state=orm.state,
            postal_code=PostalCode(orm.postal_code),
            country=orm.country or "India",
        )

    return Supplier(
        id=SupplierId(orm.id),
        code=SupplierCode(orm.code),
        name=SupplierName(orm.name),
        phone=PhoneNumber(orm.phone),
        email=EmailAddress(orm.email) if orm.email else None,
        address=address,
        gstin=GSTIN(orm.gstin) if orm.gstin else None,
        pan=PAN(orm.pan) if orm.pan else None,
        status=SupplierStatus(orm.status),
        category=SupplierCategory(orm.category),
        created_at=orm.created_at,
        updated_at=orm.updated_at,
        version=orm.version,
    )
