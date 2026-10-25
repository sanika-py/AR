"""Create audio-free storage and audit tables.

Revision ID: 0001_initial_storage
Revises:
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial_storage"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "officers",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("username", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=256), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "role IN ('officer', 'supervisor', 'admin')", name="ck_officers_role"
        ),
    )
    op.create_index("ix_officers_username", "officers", ["username"], unique=True)

    op.create_table(
        "calls",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("assigned_team", sa.String(length=120)),
        sa.Column("escalated", sa.Boolean(), nullable=False),
        sa.Column("escalation_count", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('active', 'escalated', 'transferred', 'closed')",
            name="ck_calls_status",
        ),
        sa.CheckConstraint("escalation_count >= 0", name="ck_calls_escalation_count"),
        sa.ForeignKeyConstraint(["created_by"], ["officers.id"]),
    )

    op.create_table(
        "summaries",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("call_id", sa.String(length=36), nullable=False),
        sa.Column("duration_seconds", sa.Float(), nullable=False),
        sa.Column("analyzed_windows", sa.Integer(), nullable=False),
        sa.Column("final_attention_category", sa.String(length=80), nullable=False),
        sa.Column("peak_distress_indicator", sa.Float(), nullable=False),
        sa.Column("peak_nervousness_indicator", sa.Float(), nullable=False),
        sa.Column("quality_flags", sa.JSON(), nullable=False),
        sa.Column("model_id", sa.String(length=200), nullable=False),
        sa.Column("model_revision", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("duration_seconds >= 0", name="ck_summaries_duration"),
        sa.CheckConstraint("analyzed_windows >= 0", name="ck_summaries_window_count"),
        sa.CheckConstraint(
            "peak_distress_indicator BETWEEN 0 AND 1",
            name="ck_summaries_peak_distress",
        ),
        sa.CheckConstraint(
            "peak_nervousness_indicator BETWEEN 0 AND 1",
            name="ck_summaries_peak_nervousness",
        ),
        sa.ForeignKeyConstraint(["call_id"], ["calls.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_summaries_call_id", "summaries", ["call_id"])

    op.create_table(
        "flags",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("call_id", sa.String(length=36), nullable=False),
        sa.Column("officer_id", sa.String(length=36), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("status IN ('open', 'reviewed')", name="ck_flags_status"),
        sa.ForeignKeyConstraint(["call_id"], ["calls.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["officer_id"], ["officers.id"]),
    )
    op.create_index("ix_flags_call_id", "flags", ["call_id"])

    op.create_table(
        "notes",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("call_id", sa.String(length=36), nullable=False),
        sa.Column("officer_id", sa.String(length=36), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["call_id"], ["calls.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["officer_id"], ["officers.id"]),
    )
    op.create_index("ix_notes_call_id", "notes", ["call_id"])

    op.create_table(
        "audit_log",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("actor_id", sa.String(length=36)),
        sa.Column("call_id", sa.String(length=36)),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["officers.id"]),
        sa.ForeignKeyConstraint(["call_id"], ["calls.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_audit_log_actor_id", "audit_log", ["actor_id"])
    op.create_index("ix_audit_log_call_id", "audit_log", ["call_id"])
    op.create_index("ix_audit_log_action", "audit_log", ["action"])
    op.create_index("ix_audit_log_created_at", "audit_log", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_audit_log_created_at", table_name="audit_log")
    op.drop_index("ix_audit_log_action", table_name="audit_log")
    op.drop_index("ix_audit_log_call_id", table_name="audit_log")
    op.drop_index("ix_audit_log_actor_id", table_name="audit_log")
    op.drop_table("audit_log")
    op.drop_index("ix_notes_call_id", table_name="notes")
    op.drop_table("notes")
    op.drop_index("ix_flags_call_id", table_name="flags")
    op.drop_table("flags")
    op.drop_index("ix_summaries_call_id", table_name="summaries")
    op.drop_table("summaries")
    op.drop_table("calls")
    op.drop_index("ix_officers_username", table_name="officers")
    op.drop_table("officers")
