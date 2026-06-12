"""Redis を用いた WebSocket ワンタイムチケットストアの実装。"""

import secrets
import uuid

import redis.asyncio as aioredis

from app.application.interfaces.auth import TicketStore
from app.domain.primitives.primitives import UserId


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

    async def create_ticket(self, user_id: UserId) -> str:
        """指定されたユーザー ID に対する一時的な接続チケットを生成・保存します。

        Args:
            user_id: 接続ユーザーの UUID。

        Returns:
            生成されたチケット文字列。
        """
        ticket = f"ws_ticket_{secrets.token_urlsafe(32)}"
        await self._redis.set(ticket, str(user_id.value), ex=10)
        return ticket

    async def consume_ticket(self, ticket: str) -> UserId | None:
        """チケットを検証し、有効な場合はユーザー ID を返してチケットを削除します。

        Args:
            ticket: 検証するチケット文字列。

        Returns:
            有効な場合は UserId、それ以外は None。
        """
        val = await self._redis.getdel(ticket)
        if val is None:
            return None

        val_str = val.decode("utf-8") if isinstance(val, bytes) else str(val)
        try:
            return UserId(uuid.UUID(val_str))
        except ValueError:
            return None
