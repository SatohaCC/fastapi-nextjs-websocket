"""Redis Pub/Sub を購読して WebSocket クライアントへ配信するサブスクライバー。"""

import asyncio
import json

import redis.asyncio as aioredis
from redis.exceptions import RedisError
from redis.exceptions import TimeoutError as RedisTimeoutError

from ...application.interfaces.connection_manager import ConnectionManager
from ...application.outbox.routing import FeedRouter
from ..config import settings
from ..serialization import dict_to_feed


async def redis_subscriber(
    connection_manager: ConnectionManager,
    feed_router: FeedRouter,
) -> None:
    """Redis の Pub/Sub を購読し、FeedRouter に配信を委譲します。

    Args:
        connection_manager: 配信を担当するサービス。
        feed_router: イベントタイプに基づいて配信戦略を解決するルーター。
    """
    print(
        f"[REDIS_SUB] Starting redis_subscriber task for channel "
        f"{settings.REDIS_CHANNEL}...",
        flush=True,
    )

    while True:
        client = None
        pubsub = None
        try:
            client = aioredis.from_url(
                settings.REDIS_URL,
                socket_timeout=None,
                socket_keepalive=True,
                health_check_interval=30,
            )
            pubsub = client.pubsub()
            await pubsub.subscribe(settings.REDIS_CHANNEL)
            print(
                f"[REDIS_SUB] Subscribed to Redis channel {settings.REDIS_CHANNEL}",
                flush=True,
            )

            async for raw in pubsub.listen():
                if raw["type"] != "message":
                    continue

                print(
                    f"[REDIS_SUB] Received raw message from Redis: {raw['data']}",
                    flush=True,
                )
                data = json.loads(raw["data"])
                feed = dict_to_feed(data)
                print(
                    f"[REDIS_SUB] Routing feed {feed.sequence_id} "
                    f"(event: {feed.event_type}) to feed_router",
                    flush=True,
                )
                await feed_router.route(feed, connection_manager)

        except (RedisTimeoutError, asyncio.TimeoutError) as e:
            print(
                f"[REDIS_SUB] Timeout reading from Redis: {e}. Reconnecting...",
                flush=True,
            )
        except RedisError as e:
            print(
                f"[REDIS_SUB] Redis error in subscriber: {e}. Reconnecting in 2s...",
                flush=True,
            )
            await asyncio.sleep(2.0)
        except Exception as e:
            print(
                f"[REDIS_SUB] Unexpected exception in subscriber: {e}. "
                f"Reconnecting in 2s...",
                flush=True,
            )
            await asyncio.sleep(2.0)
        finally:
            if pubsub is not None:
                try:
                    await pubsub.unsubscribe(settings.REDIS_CHANNEL)
                except Exception:
                    pass
            if client is not None:
                try:
                    await client.close()
                except Exception:
                    pass
