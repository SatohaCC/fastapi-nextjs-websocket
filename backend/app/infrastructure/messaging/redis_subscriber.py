"""Redis Pub/Sub を購読して WebSocket クライアントへ配信するサブスクライバー。"""

import json

import redis.asyncio as aioredis

from ...domain.repositories.connection_manager import ConnectionManager
from ...domain.services.feed_routing import FeedRouter
from ..config import settings


async def redis_subscriber(
    connection_manager: ConnectionManager,
    feed_router: FeedRouter,
) -> None:
    """Redis の Pub/Sub を購読し、FeedRouter に配信を委譲します。

    サブスクライバー自体はイベントタイプの解釈を一切行わず、
    「受け取って FeedRouter に渡すだけ」のシンプルな役割に徹します。

    Args:
        connection_manager: 配信を担当するサービス。
        feed_router: イベントタイプに基づいて配信戦略を解決するルーター。
    """
    client: aioredis.Redis = aioredis.from_url(settings.REDIS_URL)
    pubsub = client.pubsub()
    await pubsub.subscribe(settings.REDIS_CHANNEL)

    try:
        async for raw in pubsub.listen():
            if raw["type"] != "message":
                continue

            data = json.loads(raw["data"])
            await feed_router.route(data, connection_manager)
    finally:
        await pubsub.unsubscribe(settings.REDIS_CHANNEL)
        await client.close()
