"""operational support layer

Revision ID: 0003_operational_layer
Revises: 0002_conversation_triage
Create Date: 2026-04-17
"""
from alembic import op
import sqlalchemy as sa


revision = "0003_operational_layer"
down_revision = "0002_conversation_triage"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("knowledge_base", sa.Column("usage_count", sa.Integer(), nullable=False, server_default="0"))

    op.execute("UPDATE tickets SET priority = 'MEDIUM' WHERE priority = 'NORMAL'")
    op.add_column("tickets", sa.Column("routing_group", sa.String(length=80), nullable=False, server_default="general"))
    op.add_column("tickets", sa.Column("first_response_at", sa.DateTime(), nullable=True))
    op.add_column("tickets", sa.Column("sla_due_at", sa.DateTime(), nullable=True))
    op.add_column("tickets", sa.Column("sla_breached", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("tickets", sa.Column("reopened_from_ticket_id", sa.Integer(), nullable=True))
    op.add_column("tickets", sa.Column("reopen_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("tickets", sa.Column("last_reopened_at", sa.DateTime(), nullable=True))
    op.create_index("ix_tickets_routing_group", "tickets", ["routing_group"])
    op.create_index("ix_tickets_priority", "tickets", ["priority"])
    op.create_index("ix_tickets_sla_due_at", "tickets", ["sla_due_at"])
    op.create_index("ix_tickets_sla_breached", "tickets", ["sla_breached"])
    op.create_foreign_key("fk_tickets_reopened_from_ticket_id", "tickets", "tickets", ["reopened_from_ticket_id"], ["id"], ondelete="SET NULL")

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ticket_id", sa.Integer(), sa.ForeignKey("tickets.id", ondelete="CASCADE"), nullable=True),
        sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action_type", sa.String(length=40), nullable=False),
        sa.Column("previous_value", sa.JSON(), nullable=True),
        sa.Column("new_value", sa.JSON(), nullable=True),
        sa.Column("summary", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_audit_logs_id", "audit_logs", ["id"])
    op.create_index("ix_audit_logs_ticket_id", "audit_logs", ["ticket_id"])
    op.create_index("ix_audit_logs_actor_user_id", "audit_logs", ["actor_user_id"])
    op.create_index("ix_audit_logs_action_type", "audit_logs", ["action_type"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recipient_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("ticket_id", sa.Integer(), sa.ForeignKey("tickets.id", ondelete="CASCADE"), nullable=True),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_notifications_id", "notifications", ["id"])
    op.create_index("ix_notifications_recipient_user_id", "notifications", ["recipient_user_id"])
    op.create_index("ix_notifications_ticket_id", "notifications", ["ticket_id"])
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"])
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"])

    op.create_table(
        "message_feedback",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("message_id", sa.Integer(), sa.ForeignKey("messages.id", ondelete="CASCADE"), nullable=False),
        sa.Column("conversation_id", sa.Integer(), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("helpful", sa.Boolean(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_message_feedback_id", "message_feedback", ["id"])
    op.create_index("ix_message_feedback_message_id", "message_feedback", ["message_id"])
    op.create_index("ix_message_feedback_conversation_id", "message_feedback", ["conversation_id"])
    op.create_index("ix_message_feedback_user_id", "message_feedback", ["user_id"])


def downgrade() -> None:
    op.drop_table("message_feedback")
    op.drop_table("notifications")
    op.drop_table("audit_logs")
    op.drop_constraint("fk_tickets_reopened_from_ticket_id", "tickets", type_="foreignkey")
    op.drop_index("ix_tickets_sla_breached", table_name="tickets")
    op.drop_index("ix_tickets_sla_due_at", table_name="tickets")
    op.drop_index("ix_tickets_priority", table_name="tickets")
    op.drop_index("ix_tickets_routing_group", table_name="tickets")
    op.drop_column("tickets", "last_reopened_at")
    op.drop_column("tickets", "reopen_count")
    op.drop_column("tickets", "reopened_from_ticket_id")
    op.drop_column("tickets", "sla_breached")
    op.drop_column("tickets", "sla_due_at")
    op.drop_column("tickets", "first_response_at")
    op.drop_column("tickets", "routing_group")
    op.drop_column("knowledge_base", "usage_count")
