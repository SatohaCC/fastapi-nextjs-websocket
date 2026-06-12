"""widen sequence_name columns for per-user DM inbox names.

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-13

per-user の DM 受信ストリーム名 ``direct_request:{username}`` を収めるため、
``delivery_feeds.sequence_name`` と ``delivery_sequences.name`` を
``String(50)`` から ``String(80)`` に拡張する。

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """sequence_name 系カラムを String(80) に拡張します。"""
    op.alter_column(
        "delivery_sequences",
        "name",
        existing_type=sa.String(length=50),
        type_=sa.String(length=80),
        existing_nullable=False,
    )
    op.alter_column(
        "delivery_feeds",
        "sequence_name",
        existing_type=sa.String(length=50),
        type_=sa.String(length=80),
        existing_nullable=False,
    )


def downgrade() -> None:
    """sequence_name 系カラムを String(50) に戻します。"""
    op.alter_column(
        "delivery_feeds",
        "sequence_name",
        existing_type=sa.String(length=80),
        type_=sa.String(length=50),
        existing_nullable=False,
    )
    op.alter_column(
        "delivery_sequences",
        "name",
        existing_type=sa.String(length=80),
        type_=sa.String(length=50),
        existing_nullable=False,
    )
