"""Bidirectional mapping functions between Purchase domain aggregate and ORM models."""
from __future__ import annotations

from evopharm_retail_erp.domain.medicine import MedicineId
from evopharm_retail_erp.domain.purchase import (
    Discount,
    InvoiceReference,
    Money,
    PaymentStatus,
    Purchase,
    PurchaseId,
    PurchaseLine,
    PurchaseLineId,
    PurchaseLineStatus,
    PurchaseOrderReference,
    PurchaseQuantity,
    PurchaseStatus,
    ReceivingStatus,
    SupplierReference,
    TaxRate,
    UnitPrice,
)
from ..models.purchase import PurchaseLineORM, PurchaseORM


def purchase_to_orm(purchase: Purchase) -> PurchaseORM:
    """Convert a Purchase aggregate root into a PurchaseORM model."""
    sup_ref = purchase.supplier_reference
    inv_ref = purchase.invoice_reference

    orm = PurchaseORM(
        id=purchase.id.value,
        supplier_id=sup_ref.supplier_id,
        supplier_code=sup_ref.code,
        supplier_name=sup_ref.name,
        order_reference=purchase.order_reference.value,
        invoice_reference=inv_ref.value if inv_ref else None,
        purchase_status=purchase.purchase_status.value,
        receiving_status=purchase.receiving_status.value,
        payment_status=purchase.payment_status.value,
        total_amount_paid=purchase.total_amount_paid.amount,
        paid_currency=purchase.total_amount_paid.currency,
        created_at=purchase.created_at,
        updated_at=purchase.updated_at,
        version=purchase.version,
    )

    orm.lines = [
        PurchaseLineORM(
            id=line.id.value,
            purchase_id=purchase.id.value,
            medicine_id=line.medicine_id.value,
            ordered_quantity=line.ordered_quantity.value,
            received_quantity=line.received_quantity.value,
            unit_price_amount=line.unit_price.amount,
            unit_price_currency=line.unit_price.value.currency,
            discount_percentage=line.discount.percentage,
            discount_fixed_amount=line.discount.fixed_amount.amount,
            tax_rate_percentage=line.tax_rate.percentage,
            status=line.status.value,
            created_at=line.created_at,
            updated_at=line.updated_at,
        )
        for line in purchase.lines
    ]

    return orm


def orm_to_purchase(orm: PurchaseORM) -> Purchase:
    """Reconstruct a Purchase aggregate root from a PurchaseORM model."""
    sup_ref = SupplierReference(
        supplier_id=orm.supplier_id,
        code=orm.supplier_code,
        name=orm.supplier_name,
    )
    inv_ref = InvoiceReference(orm.invoice_reference) if orm.invoice_reference else None

    lines_dict: dict = {}
    for l_orm in orm.lines:
        line = PurchaseLine(
            id=PurchaseLineId(l_orm.id),
            medicine_id=MedicineId(l_orm.medicine_id),
            ordered_quantity=PurchaseQuantity(l_orm.ordered_quantity),
            received_quantity=PurchaseQuantity(l_orm.received_quantity),
            unit_price=UnitPrice(Money(l_orm.unit_price_amount, l_orm.unit_price_currency)),
            discount=Discount(
                percentage=l_orm.discount_percentage,
                fixed_amount=Money(l_orm.discount_fixed_amount, l_orm.unit_price_currency),
            ),
            tax_rate=TaxRate(l_orm.tax_rate_percentage),
            status=PurchaseLineStatus(l_orm.status),
            created_at=l_orm.created_at,
            updated_at=l_orm.updated_at,
        )
        lines_dict[line.id.value] = line

    purchase = Purchase(
        id=PurchaseId(orm.id),
        supplier_reference=sup_ref,
        order_reference=PurchaseOrderReference(orm.order_reference),
        invoice_reference=inv_ref,
        purchase_status=PurchaseStatus(orm.purchase_status),
        receiving_status=ReceivingStatus(orm.receiving_status),
        payment_status=PaymentStatus(orm.payment_status),
        total_amount_paid=Money(orm.total_amount_paid, orm.paid_currency),
        created_at=orm.created_at,
        updated_at=orm.updated_at,
        version=orm.version,
    )

    object.__setattr__(purchase, "_lines", lines_dict)
    return purchase
