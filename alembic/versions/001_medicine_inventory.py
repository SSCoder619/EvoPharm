"""Initial migration for Medicine and Inventory bounded contexts

Revision ID: 001_medicine_inventory
Revises: 
Create Date: 2026-08-09 01:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_medicine_inventory'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Medicine master table
    op.create_table(
        'medicine_masters',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('generic_name', sa.String(length=200), nullable=False),
        sa.Column('composition_json', sa.Text(), nullable=False),
        sa.Column('manufacturer', sa.String(length=200), nullable=False),
        sa.Column('hsn_code', sa.String(length=20), nullable=False),
        sa.Column('pack_size', sa.Integer(), nullable=False),
        sa.Column('unit_of_measure', sa.String(length=50), nullable=False),
        sa.Column('dosage_form', sa.String(length=50), nullable=False),
        sa.Column('schedule', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('storage_min_temp', sa.Float(), nullable=True),
        sa.Column('storage_max_temp', sa.Float(), nullable=True),
        sa.Column('storage_max_humidity', sa.Float(), nullable=True),
        sa.Column('storage_refrigeration', sa.Boolean(), nullable=True),
        sa.Column('storage_protect_light', sa.Boolean(), nullable=True),
        sa.Column('storage_instructions', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_medicine_masters_generic_name'), 'medicine_masters', ['generic_name'], unique=False)
    op.create_index(op.f('ix_medicine_masters_hsn_code'), 'medicine_masters', ['hsn_code'], unique=False)
    op.create_index(op.f('ix_medicine_masters_name'), 'medicine_masters', ['name'], unique=False)
    op.create_index(op.f('ix_medicine_masters_status'), 'medicine_masters', ['status'], unique=False)

    # Medicine barcodes
    op.create_table(
        'medicine_barcodes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('medicine_id', sa.Uuid(), nullable=False),
        sa.Column('barcode_value', sa.String(length=100), nullable=False),
        sa.Column('barcode_type', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['medicine_id'], ['medicine_masters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_medicine_barcodes_barcode_value'), 'medicine_barcodes', ['barcode_value'], unique=False)
    op.create_index(op.f('ix_medicine_barcodes_medicine_id'), 'medicine_barcodes', ['medicine_id'], unique=False)

    # Medicine alternate names
    op.create_table(
        'medicine_alternate_names',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('medicine_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.ForeignKeyConstraint(['medicine_id'], ['medicine_masters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_medicine_alternate_names_medicine_id'), 'medicine_alternate_names', ['medicine_id'], unique=False)
    op.create_index(op.f('ix_medicine_alternate_names_name'), 'medicine_alternate_names', ['name'], unique=False)

    # Medicine batches
    op.create_table(
        'medicine_batches',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('medicine_id', sa.Uuid(), nullable=False),
        sa.Column('batch_number', sa.String(length=100), nullable=False),
        sa.Column('manufacturing_date', sa.Date(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=False),
        sa.Column('received_date', sa.Date(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('quarantine_reason', sa.String(length=100), nullable=True),
        sa.Column('adjustment_reason', sa.String(length=100), nullable=True),
        sa.Column('recall_note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['medicine_id'], ['medicine_masters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_medicine_batches_batch_number'), 'medicine_batches', ['batch_number'], unique=False)
    op.create_index(op.f('ix_medicine_batches_expiry_date'), 'medicine_batches', ['expiry_date'], unique=False)
    op.create_index(op.f('ix_medicine_batches_medicine_id'), 'medicine_batches', ['medicine_id'], unique=False)
    op.create_index(op.f('ix_medicine_batches_status'), 'medicine_batches', ['status'], unique=False)

    # Inventory projections
    op.create_table(
        'inventory_projections',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('medicine_id', sa.Uuid(), nullable=False),
        sa.Column('medicine_batch_id', sa.Uuid(), nullable=False),
        sa.Column('quantity_on_hand', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('quantity_reserved', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reorder_level', sa.Integer(), nullable=True),
        sa.Column('min_stock_level', sa.Integer(), nullable=True),
        sa.Column('max_stock_level', sa.Integer(), nullable=True),
        sa.Column('overstock_level', sa.Integer(), nullable=True),
        sa.Column('last_movement_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_projections_medicine_batch_id'), 'inventory_projections', ['medicine_batch_id'], unique=False)
    op.create_index(op.f('ix_inventory_projections_medicine_id'), 'inventory_projections', ['medicine_id'], unique=False)

    # Stock movements
    op.create_table(
        'stock_movements',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('inventory_id', sa.Uuid(), nullable=False),
        sa.Column('medicine_id', sa.Uuid(), nullable=False),
        sa.Column('medicine_batch_id', sa.Uuid(), nullable=False),
        sa.Column('movement_type', sa.String(length=50), nullable=False),
        sa.Column('direction', sa.String(length=50), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('source_document_type', sa.String(length=50), nullable=True),
        sa.Column('source_document_id', sa.Uuid(), nullable=True),
        sa.Column('source_document_reference', sa.String(length=100), nullable=True),
        sa.Column('reason', sa.String(length=200), nullable=True),
        sa.Column('performed_by_user_id', sa.Uuid(), nullable=True),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['inventory_id'], ['inventory_projections.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stock_movements_inventory_id'), 'stock_movements', ['inventory_id'], unique=False)
    op.create_index(op.f('ix_stock_movements_medicine_batch_id'), 'stock_movements', ['medicine_batch_id'], unique=False)
    op.create_index(op.f('ix_stock_movements_medicine_id'), 'stock_movements', ['medicine_id'], unique=False)
    op.create_index(op.f('ix_stock_movements_source_document_id'), 'stock_movements', ['source_document_id'], unique=False)


def downgrade() -> None:
    op.drop_table('stock_movements')
    op.drop_table('inventory_projections')
    op.drop_table('medicine_batches')
    op.drop_table('medicine_alternate_names')
    op.drop_table('medicine_barcodes')
    op.drop_table('medicine_masters')
