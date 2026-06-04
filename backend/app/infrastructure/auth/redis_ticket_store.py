"""Redis を用いた WebSocket ワンタイムチケットストアの実装。"""

import secrets

import redis.asyncio as aioredis

from app.application.interfaces.auth import TicketStore
from app.domain.primitives.primitives import Username


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

    async def create_ticket(self, username: Username) -> str:
        """指定されたユーザーに対する一時的な接続チケットを生成・保存します（有効期限10秒）。

        Args:
            username: 接続ユーザー名。

        Returns:
            生成されたチケット文字列。
        """
        ticket = f"ws_ticket_{secrets.token_urlsafe(32)}"
        await self._redis.set(ticket, username.value, ex=10)
        return ticket

    async def consume_ticket(self, ticket: str) -> Username | None:
        """チケットを検証し、有効な場合は対応するユーザー名を返し、チケットを即時削除します。

        Args:
            ticket: 検証するチケット文字列。

        Returns:
            有効な場合は Username、それ以外は None。
        """
        val = await self._redis.getdel(ticket)
        if val is None:
            return None

        val_str = val.decode("utf-8") if isinstance(val, bytes) else str(val)
        return Username(val_str)
