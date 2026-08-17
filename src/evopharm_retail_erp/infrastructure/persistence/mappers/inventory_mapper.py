"""Bidirectional mapping functions between Inventory domain aggregate and ORM models."""
from __future__ import annotations

from evopharm_retail_erp.domain.inventory import (
    Inventory,
    InventoryId,
    MovementDirection,
    MovementQuantity,
    MovementReason,
    MovementType,
    Quantity,
    ReorderLevel,
    SafetyStock,
    SourceDocumentRef,
    StockMovement,
    StockMovementId,
    StockThresholds,
)
from evopharm_retail_erp.domain.medicine import MedicineBatchId, MedicineId
from ..models.inventory import InventoryORM, StockMovementORM


def inventory_to_orm(inventory: Inventory) -> InventoryORM:
    """Convert an Inventory aggregate root into an InventoryORM model."""
    t = inventory.thresholds
    orm = InventoryORM(
        id=inventory.id.value,
        medicine_id=inventory.medicine_id.value,
        medicine_batch_id=inventory.medicine_batch_id.value,
        quantity_on_hand=inventory.quantity_on_hand.value,
        quantity_reserved=inventory.quantity_reserved.value,
        reorder_level=t.reorder_level.value if t and t.reorder_level else None,
        min_stock_level=t.minimum_level.value if t and t.minimum_level else None,
        max_stock_level=None,
        overstock_level=t.overstock_level.value if t and t.overstock_level else None,
        last_movement_at=inventory.last_movement_at,
        created_at=inventory.created_at,
        updated_at=inventory.updated_at,
        version=inventory.version,
    )

    orm.movements = [
        StockMovementORM(
            id=m.id.value,
            inventory_id=inventory.id.value,
            medicine_id=m.medicine_id.value,
            medicine_batch_id=m.medicine_batch_id.value,
            movement_type=m.movement_type.value,
            direction=m.direction.value,
            quantity=m.quantity.value,
            source_document_type=m.source_document.document_type if m.source_document else None,
            source_document_id=m.source_document.document_id if m.source_document else None,
            source_document_reference=m.source_document.reference_number if m.source_document else None,
            reason=m.reason.description if m.reason else None,
            performed_by_user_id=m.performed_by_user_id,
            occurred_at=m.occurred_at,
        )
        for m in inventory.movements
    ]

    return orm


def orm_to_inventory(orm: InventoryORM) -> Inventory:
    """Reconstruct an Inventory aggregate root from an InventoryORM model."""
    thresholds = None
    if orm.reorder_level is not None and orm.overstock_level is not None:
        thresholds = StockThresholds.create(
            reorder_level=orm.reorder_level,
            overstock_level=orm.overstock_level,
            minimum_level=orm.min_stock_level if orm.min_stock_level is not None else 0,
        )

    movements_list: list[StockMovement] = []
    for m_orm in orm.movements:
        doc = None
        if m_orm.source_document_type and m_orm.source_document_id and m_orm.source_document_reference:
            doc = SourceDocumentRef(
                document_type=m_orm.source_document_type,
                document_id=m_orm.source_document_id,
                reference_number=m_orm.source_document_reference,
            )

        m = StockMovement(
            id=StockMovementId(m_orm.id),
            inventory_id=InventoryId(m_orm.inventory_id),
            medicine_id=MedicineId(m_orm.medicine_id),
            medicine_batch_id=MedicineBatchId(m_orm.medicine_batch_id),
            movement_type=MovementType(m_orm.movement_type),
            direction=MovementDirection(m_orm.direction),
            quantity=MovementQuantity(m_orm.quantity),
            source_document=doc,
            reason=MovementReason(m_orm.reason) if m_orm.reason else None,
            performed_by_user_id=m_orm.performed_by_user_id,
            occurred_at=m_orm.occurred_at,
        )
        movements_list.append(m)

    inv = Inventory(
        id=InventoryId(orm.id),
        medicine_id=MedicineId(orm.medicine_id),
        medicine_batch_id=MedicineBatchId(orm.medicine_batch_id),
        quantity_on_hand=Quantity(orm.quantity_on_hand),
        quantity_reserved=Quantity(orm.quantity_reserved),
        thresholds=thresholds,
        last_movement_at=orm.last_movement_at,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
        version=orm.version,
    )
    object.__setattr__(inv, "_movements", movements_list)
    return inv
