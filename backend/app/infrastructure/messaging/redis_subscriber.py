"""Redis Pub/Sub を購読して WebSocket クライアントへ配信するサブスクライバー。"""

import json

import redis.asyncio as aioredis

from ...domain.repositories.connection_manager import ConnectionManager
from ..config import settings


async def redis_subscriber(connection_manager: ConnectionManager) -> None:
    """Redis の Pub/Sub を購読し、受け取ったイベントの種類に応じて
    WebSocket クライアントに適切に配信します。

    Args:
        connection_manager (ConnectionManager): 配信を担当するサービス。
            具象クラス（ChatManager）に依存せず、インターフェースを介して操作します。
    """
    client: aioredis.Redis = aioredis.from_url(settings.REDIS_URL)
    pubsub = client.pubsub()
    await pubsub.subscribe(settings.REDIS_CHANNEL)

    try:
        async for raw in pubsub.listen():
            if raw["type"] != "message":
                continue

            data = json.loads(raw["data"])
            event_type = data.get("type")

            if event_type in ("message", "join", "leave"):
                # チャット関連は全員に放送
                await connection_manager.broadcast(data)

            elif event_type in ("request", "request_updated"):
                # リクエスト関連は関係者のみに送信
                sender = data.get("sender")
                recipient = data.get("recipient")

                if sender:
                    await connection_manager.send_to_user(sender, data)
                if recipient and recipient != sender:
                    await connection_manager.send_to_user(recipient, data)
    finally:
        await pubsub.unsubscribe(settings.REDIS_CHANNEL)
        await client.close()
