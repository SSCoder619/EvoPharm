"""Migration for Purchase and Supplier bounded contexts

Revision ID: 002_purchase_supplier
Revises: 001_medicine_inventory
Create Date: 2026-08-09 02:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_purchase_supplier'
down_revision: Union[str, None] = '001_medicine_inventory'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Suppliers table
    op.create_table(
        'suppliers',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('street', sa.String(length=200), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('gstin', sa.String(length=20), nullable=True),
        sa.Column('pan', sa.String(length=20), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_suppliers_code'), 'suppliers', ['code'], unique=True)
    op.create_index(op.f('ix_suppliers_gstin'), 'suppliers', ['gstin'], unique=False)
    op.create_index(op.f('ix_suppliers_name'), 'suppliers', ['name'], unique=False)
    op.create_index(op.f('ix_suppliers_status'), 'suppliers', ['status'], unique=False)

    # Purchase orders table
    op.create_table(
        'purchase_orders',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('supplier_id', sa.Uuid(), nullable=False),
        sa.Column('supplier_code', sa.String(length=50), nullable=True),
        sa.Column('supplier_name', sa.String(length=200), nullable=True),
        sa.Column('order_reference', sa.String(length=100), nullable=False),
        sa.Column('invoice_reference', sa.String(length=100), nullable=True),
        sa.Column('purchase_status', sa.String(length=50), nullable=False),
        sa.Column('receiving_status', sa.String(length=50), nullable=False),
        sa.Column('payment_status', sa.String(length=50), nullable=False),
        sa.Column('total_amount_paid', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0.00'),
        sa.Column('paid_currency', sa.String(length=10), nullable=False, server_default='INR'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_purchase_orders_invoice_reference'), 'purchase_orders', ['invoice_reference'], unique=False)
    op.create_index(op.f('ix_purchase_orders_order_reference'), 'purchase_orders', ['order_reference'], unique=True)
    op.create_index(op.f('ix_purchase_orders_payment_status'), 'purchase_orders', ['payment_status'], unique=False)
    op.create_index(op.f('ix_purchase_orders_purchase_status'), 'purchase_orders', ['purchase_status'], unique=False)
    op.create_index(op.f('ix_purchase_orders_receiving_status'), 'purchase_orders', ['receiving_status'], unique=False)
    op.create_index(op.f('ix_purchase_orders_supplier_id'), 'purchase_orders', ['supplier_id'], unique=False)

    # Purchase order lines table
    op.create_table(
        'purchase_order_lines',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('purchase_id', sa.Uuid(), nullable=False),
        sa.Column('medicine_id', sa.Uuid(), nullable=False),
        sa.Column('ordered_quantity', sa.Integer(), nullable=False),
        sa.Column('received_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('unit_price_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('unit_price_currency', sa.String(length=10), nullable=False, server_default='INR'),
        sa.Column('discount_percentage', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0.00'),
        sa.Column('discount_fixed_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0.00'),
        sa.Column('tax_rate_percentage', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0.00'),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['purchase_id'], ['purchase_orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_purchase_order_lines_medicine_id'), 'purchase_order_lines', ['medicine_id'], unique=False)
    op.create_index(op.f('ix_purchase_order_lines_purchase_id'), 'purchase_order_lines', ['purchase_id'], unique=False)


def downgrade() -> None:
    op.drop_table('purchase_order_lines')
    op.drop_table('purchase_orders')
    op.drop_table('suppliers')
