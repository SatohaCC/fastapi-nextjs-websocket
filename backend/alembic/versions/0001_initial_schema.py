"""initial schema.

Revision ID: 0001
Revises:
Create Date: 2026-06-06

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """全テーブルを作成します。"""
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sender", sa.String(length=50), nullable=False),
        sa.Column("recipient", sa.String(length=50), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "delivery_sequences",
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("last_id", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("name"),
    )

    op.create_table(
        "delivery_feeds",
        sa.Column("sequence_name", sa.String(length=50), nullable=False),
        sa.Column("sequence_id", sa.BigInteger(), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("sequence_name", "sequence_id"),
    )
    op.create_index(
        "ix_delivery_feeds_status_seq",
        "delivery_feeds",
        ["status", "sequence_name", "sequence_id"],
    )

    op.create_table(
        "user_settings",
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("global_chat", sa.Boolean(), nullable=False),
        sa.Column("direct_request", sa.Boolean(), nullable=False),
        sa.Column("direct_request_updated", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("username"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("hashed_password", sa.String(length=60), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )


def downgrade() -> None:
    """全テーブルを削除します。"""
    op.drop_table("users")
    op.drop_table("user_settings")
    op.drop_index("ix_delivery_feeds_status_seq", table_name="delivery_feeds")
    op.drop_table("delivery_feeds")
    op.drop_table("delivery_sequences")
    op.drop_table("tasks")
    op.drop_table("messages")
