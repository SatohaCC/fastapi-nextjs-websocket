"""add browser_notification column to user_settings.

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-07

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """user_settings テーブルに browser_notification カラムを追加します。"""
    op.add_column(
        "user_settings",
        sa.Column(
            "browser_notification", sa.Boolean(), nullable=False, server_default="false"
        ),
    )


def downgrade() -> None:
    """browser_notification カラムを削除します。"""
    op.drop_column("user_settings", "browser_notification")
