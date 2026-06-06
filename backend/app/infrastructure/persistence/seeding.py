"""データベースの初期データシード処理。"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.infrastructure.auth.password_hasher import PasswordHasher
from app.infrastructure.config import settings


async def seed_users(conn: AsyncConnection) -> None:
    """ユーザー初期レコードのシードを行います（空の場合のみ）。

    Args:
        conn: SQLAlchemy の非同期コネクション。
    """
    result = await conn.execute(text("SELECT COUNT(*) FROM users"))
    if result.scalar() == 0:
        for username, password in settings.USERS.items():
            user_id = uuid.uuid7()
            hashed = PasswordHasher.hash_password(password.value)
            await conn.execute(
                text(
                    "INSERT INTO users (id, username, hashed_password, created_at) "
                    "VALUES (:id, :username, :hashed_password, :created_at)"
                ).bindparams(
                    id=user_id,
                    username=username.value,
                    hashed_password=hashed,
                    created_at=datetime.now(timezone.utc),
                )
            )
