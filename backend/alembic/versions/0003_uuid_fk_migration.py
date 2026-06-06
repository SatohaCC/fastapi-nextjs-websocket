"""uuid_fk_migration: messages/tasks に UUID FK 追加、user_settings PK 変更。

Revision ID: 0003
Revises: 22cec7d94e56
Create Date: 2026-06-06

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003"
down_revision: str | Sequence[str] | None = "22cec7d94e56"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """UUID FK 追加・UserSettings PK 変更・データ移行を行います。"""
    # --- messages: user_id 列を追加 ---
    op.add_column(
        "messages",
        sa.Column("user_id", sa.UUID(), nullable=True),
    )
    # 既存行: username で users テーブルを参照して user_id を埋める
    op.execute(
        """
        UPDATE messages m
        SET user_id = u.id
        FROM users u
        WHERE u.username = m.username
        """
    )
    op.alter_column("messages", "user_id", nullable=False)
    op.create_foreign_key(
        "fk_messages_user_id",
        "messages",
        "users",
        ["user_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    # --- tasks: sender_id / recipient_id 列を追加 ---
    op.add_column(
        "tasks",
        sa.Column("sender_id", sa.UUID(), nullable=True),
    )
    op.add_column(
        "tasks",
        sa.Column("recipient_id", sa.UUID(), nullable=True),
    )
    # 既存行: sender/recipient 文字列から UUID を解決
    op.execute(
        """
        UPDATE tasks t
        SET sender_id = u.id
        FROM users u
        WHERE u.username = t.sender
        """
    )
    op.execute(
        """
        UPDATE tasks t
        SET recipient_id = u.id
        FROM users u
        WHERE u.username = t.recipient
        """
    )
    op.alter_column("tasks", "sender_id", nullable=False)
    op.alter_column("tasks", "recipient_id", nullable=False)
    op.create_foreign_key(
        "fk_tasks_sender_id",
        "tasks",
        "users",
        ["sender_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_tasks_recipient_id",
        "tasks",
        "users",
        ["recipient_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    # --- user_settings: PK を username → user_id に変更 ---
    # 1. user_id 列を追加（nullable で追加してデータを埋めてから NOT NULL にする）
    op.add_column(
        "user_settings",
        sa.Column("user_id", sa.UUID(), nullable=True),
    )
    op.execute(
        """
        UPDATE user_settings us
        SET user_id = u.id
        FROM users u
        WHERE u.username = us.username
        """
    )
    # username に対応する users レコードがない孤立行を削除
    op.execute(
        """
        DELETE FROM user_settings
        WHERE user_id IS NULL
        """
    )
    op.alter_column("user_settings", "user_id", nullable=False)

    # 2. 古い PK 制約を削除して新しい PK に付け替える
    op.drop_constraint("user_settings_pkey", "user_settings", type_="primary")
    op.create_primary_key("user_settings_pkey", "user_settings", ["user_id"])
    op.create_foreign_key(
        "fk_user_settings_user_id",
        "user_settings",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # 3. username 列を削除
    op.drop_column("user_settings", "username")

    # --- delivery_feeds: payload (JSONB) の sender_id / recipient_id を埋める ---
    op.execute(
        """
        UPDATE delivery_feeds
        SET payload = payload || jsonb_build_object(
            'sender_id', (
                SELECT id::text FROM users WHERE username = payload->>'sender'
            ),
            'recipient_id', (
                SELECT id::text FROM users WHERE username = payload->>'recipient'
            )
        )
        WHERE event_type = 'direct_request';
        """
    )
    op.execute(
        """
        UPDATE delivery_feeds
        SET payload = payload || jsonb_build_object(
            'sender_id', (
                SELECT id::text FROM users WHERE username = payload->>'sender'
            ),
            'recipient_id', (
                SELECT id::text FROM users WHERE username = payload->>'recipient'
            )
        )
        WHERE event_type = 'direct_request_updated';
        """
    )


def downgrade() -> None:
    """変更を元に戻します。"""
    # --- user_settings: user_id → username に戻す ---
    op.add_column(
        "user_settings",
        sa.Column("username", sa.String(length=50), nullable=True),
    )
    op.execute(
        """
        UPDATE user_settings us
        SET username = u.username
        FROM users u
        WHERE u.id = us.user_id
        """
    )
    op.alter_column("user_settings", "username", nullable=False)
    op.drop_constraint("fk_user_settings_user_id", "user_settings", type_="foreignkey")
    op.drop_constraint("user_settings_pkey", "user_settings", type_="primary")
    op.create_primary_key("user_settings_pkey", "user_settings", ["username"])
    op.drop_column("user_settings", "user_id")

    # --- tasks: sender_id / recipient_id を削除 ---
    op.drop_constraint("fk_tasks_recipient_id", "tasks", type_="foreignkey")
    op.drop_constraint("fk_tasks_sender_id", "tasks", type_="foreignkey")
    op.drop_column("tasks", "recipient_id")
    op.drop_column("tasks", "sender_id")

    # --- messages: user_id を削除 ---
    op.drop_constraint("fk_messages_user_id", "messages", type_="foreignkey")
    op.drop_column("messages", "user_id")

    # --- delivery_feeds: payload (JSONB) の sender_id / recipient_id を削除する ---
    op.execute(
        """
        UPDATE delivery_feeds
        SET payload = payload - 'sender_id' - 'recipient_id'
        WHERE event_type IN ('direct_request', 'direct_request_updated');
        """
    )
