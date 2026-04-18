"""workflow extensions

Revision ID: 0005_workflow_extensions
Revises: 0004_expand_ticket_enum_columns
Create Date: 2026-04-18
"""
from alembic import op
import sqlalchemy as sa


revision = "0005_workflow_extensions"
down_revision = "0004_expand_ticket_enum_columns"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tickets", sa.Column("request_type", sa.String(length=40), nullable=False, server_default="SUPPORT"))
    op.add_column("tickets", sa.Column("assignment_source", sa.String(length=20), nullable=True))
    op.add_column("tickets", sa.Column("assigned_at", sa.DateTime(), nullable=True))
    op.add_column("tickets", sa.Column("requested_software", sa.String(length=180), nullable=True))
    op.add_column("tickets", sa.Column("request_reason", sa.Text(), nullable=True))
    op.add_column("tickets", sa.Column("request_device", sa.String(length=160), nullable=True))
    op.add_column("tickets", sa.Column("approval_required", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("tickets", sa.Column("approval_status", sa.String(length=40), nullable=False, server_default="NOT_REQUIRED"))
    op.add_column("tickets", sa.Column("approved_by_id", sa.Integer(), nullable=True))
    op.add_column("tickets", sa.Column("approved_at", sa.DateTime(), nullable=True))
    op.add_column("tickets", sa.Column("approval_notes", sa.Text(), nullable=True))
    op.create_index("ix_tickets_request_type", "tickets", ["request_type"])
    op.create_index("ix_tickets_approval_required", "tickets", ["approval_required"])
    op.create_index("ix_tickets_approval_status", "tickets", ["approval_status"])
    op.create_index("ix_tickets_approved_by_id", "tickets", ["approved_by_id"])
    op.create_foreign_key("fk_tickets_approved_by_id", "tickets", "users", ["approved_by_id"], ["id"], ondelete="SET NULL")

    op.create_table(
        "ticket_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ticket_id", sa.Integer(), sa.ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("sender_role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_ticket_messages_id", "ticket_messages", ["id"])
    op.create_index("ix_ticket_messages_ticket_id", "ticket_messages", ["ticket_id"])
    op.create_index("ix_ticket_messages_sender_id", "ticket_messages", ["sender_id"])
    op.create_index("ix_ticket_messages_sender_role", "ticket_messages", ["sender_role"])
    op.create_index("ix_ticket_messages_created_at", "ticket_messages", ["created_at"])


def downgrade() -> None:
    op.drop_table("ticket_messages")
    op.drop_constraint("fk_tickets_approved_by_id", "tickets", type_="foreignkey")
    op.drop_index("ix_tickets_approved_by_id", table_name="tickets")
    op.drop_index("ix_tickets_approval_status", table_name="tickets")
    op.drop_index("ix_tickets_approval_required", table_name="tickets")
    op.drop_index("ix_tickets_request_type", table_name="tickets")
    op.drop_column("tickets", "approval_notes")
    op.drop_column("tickets", "approved_at")
    op.drop_column("tickets", "approved_by_id")
    op.drop_column("tickets", "approval_status")
    op.drop_column("tickets", "approval_required")
    op.drop_column("tickets", "request_device")
    op.drop_column("tickets", "request_reason")
    op.drop_column("tickets", "requested_software")
    op.drop_column("tickets", "assigned_at")
    op.drop_column("tickets", "assignment_source")
    op.drop_column("tickets", "request_type")
