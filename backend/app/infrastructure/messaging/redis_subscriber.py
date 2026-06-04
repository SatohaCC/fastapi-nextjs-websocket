"""Redis Pub/Sub を購読して WebSocket クライアントへ配信するサブスクライバー。"""

import asyncio
import json
import logging

import redis.asyncio as aioredis
from redis.exceptions import RedisError
from redis.exceptions import TimeoutError as RedisTimeoutError

from ...application.interfaces.connection_manager import ConnectionManager
from ...application.outbox.routing import FeedRouter
from ..config import settings
from ..serialization import dict_to_feed

logger = logging.getLogger(__name__)


async def redis_subscriber(
    connection_manager: ConnectionManager,
    feed_router: FeedRouter,
) -> None:
    """Redis の Pub/Sub を購読し、FeedRouter に配信を委譲します。

    Args:
        connection_manager: 配信を担当するサービス。
        feed_router: イベントタイプに基づいて配信戦略を解決するルーター。
    """
    logger.info(
        "Starting redis_subscriber task for channel %s...",
        settings.REDIS_CHANNEL,
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
            logger.info(
                "Subscribed to Redis channel %s",
                settings.REDIS_CHANNEL,
            )

            async for raw in pubsub.listen():
                if raw["type"] != "message":
                    continue

                logger.debug(
                    "Received raw message from Redis: %s",
                    raw["data"],
                )
                data = json.loads(raw["data"])
                feed = dict_to_feed(data)
                logger.debug(
                    "Routing feed %s (event: %s) to feed_router",
                    feed.sequence_id,
                    feed.event_type,
                )
                await feed_router.route(feed, connection_manager)

        except (RedisTimeoutError, asyncio.TimeoutError) as e:
            logger.warning(
                "Timeout reading from Redis: %s. Reconnecting...",
                e,
            )
        except RedisError as e:
            logger.error(
                "Redis error in subscriber: %s. Reconnecting in 2s...",
                e,
            )
            await asyncio.sleep(2.0)
        except Exception as e:
            logger.exception(
                "Unexpected exception in subscriber: %s. Reconnecting in 2s...",
                e,
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
