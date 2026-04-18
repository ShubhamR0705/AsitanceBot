"""expand ticket enum column lengths

Revision ID: 0004_expand_ticket_enum_columns
Revises: 0003_operational_layer
Create Date: 2026-04-18
"""
from alembic import op
import sqlalchemy as sa


revision = "0004_expand_ticket_enum_columns"
down_revision = "0003_operational_layer"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("tickets", "status", existing_type=sa.String(length=16), type_=sa.String(length=32), existing_nullable=False)
    op.alter_column("tickets", "priority", existing_type=sa.String(length=6), type_=sa.String(length=16), existing_nullable=False)


def downgrade() -> None:
    op.alter_column("tickets", "priority", existing_type=sa.String(length=16), type_=sa.String(length=8), existing_nullable=False)
    op.alter_column("tickets", "status", existing_type=sa.String(length=32), type_=sa.String(length=16), existing_nullable=False)
