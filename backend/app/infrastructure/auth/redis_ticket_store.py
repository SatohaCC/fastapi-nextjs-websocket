"""Redis を用いた WebSocket ワンタイムチケットストアの実装。"""

import json
import secrets
import uuid

import redis.asyncio as aioredis

from app.application.interfaces.auth import TicketStore
from app.domain.primitives.primitives import SessionId, UserId


class RedisTicketStore(TicketStore):
    """Redis を用いた WebSocket ワンタイムチケットストアの実装。"""

    def __init__(self, redis_url: str) -> None:
        """チケットストアを初期化します。

        Args:
            redis_url: 接続先 Redis の URL。
        """
        self._redis: aioredis.Redis = aioredis.from_url(
            redis_url, socket_keepalive=True, health_check_interval=30
        )

    async def create_ticket(
        self, user_id: UserId, session_id: SessionId | None = None
    ) -> str:
        """指定されたユーザー ID（とセッション ID）に対する
        一時的な接続チケットを生成・保存します。

        Args:
            user_id: 接続ユーザーの UUID。
            session_id: 発行元アクセストークンに紐づくセッション ID。

        Returns:
            生成されたチケット文字列。
        """
        ticket = f"ws_ticket_{secrets.token_urlsafe(32)}"
        payload = {
            "user_id": str(user_id.value),
            "session_id": str(session_id.value) if session_id else None,
        }
        await self._redis.set(ticket, json.dumps(payload), ex=10)
        return ticket

    async def consume_ticket(
        self, ticket: str
    ) -> tuple[UserId, SessionId | None] | None:
        """チケットを検証し、有効な場合は
        (ユーザー ID, セッション ID) を返してチケットを削除します。

        Args:
            ticket: 検証するチケット文字列。

        Returns:
            有効な場合は (UserId, SessionId | None)、それ以外は None。
        """
        val = await self._redis.getdel(ticket)
        if val is None:
            return None

        val_str = val.decode("utf-8") if isinstance(val, bytes) else str(val)
        try:
            payload = json.loads(val_str)
            user_id = UserId(uuid.UUID(payload["user_id"]))
            session_id_str = payload.get("session_id")
            session_id = (
                SessionId(uuid.UUID(session_id_str)) if session_id_str else None
            )
        except ValueError, KeyError, json.JSONDecodeError, TypeError:
            return None
        return user_id, session_id
