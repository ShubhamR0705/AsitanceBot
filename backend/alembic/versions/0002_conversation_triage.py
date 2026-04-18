"""conversation triage state

Revision ID: 0002_conversation_triage
Revises: 0001_initial
Create Date: 2026-04-17
"""
from alembic import op
import sqlalchemy as sa


revision = "0002_conversation_triage"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("conversations", sa.Column("triage_stage", sa.String(length=32), nullable=False, server_default="INTAKE"))
    op.add_column("conversations", sa.Column("collected_context", sa.JSON(), nullable=True))
    op.add_column("conversations", sa.Column("last_triage", sa.JSON(), nullable=True))
    op.add_column("conversations", sa.Column("escalation_summary", sa.Text(), nullable=True))
    op.create_index("ix_conversations_triage_stage", "conversations", ["triage_stage"])
    op.alter_column("conversations", "triage_stage", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_conversations_triage_stage", table_name="conversations")
    op.drop_column("conversations", "escalation_summary")
    op.drop_column("conversations", "last_triage")
    op.drop_column("conversations", "collected_context")
    op.drop_column("conversations", "triage_stage")
