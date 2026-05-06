"""Redis Pub/Sub を使用したイベントパブリッシャーの実装。"""

import json

import redis.asyncio as aioredis

from ..config import settings


class RedisEventPublisher:
    """Redis の Pub/Sub を使用してイベントを配信するクラス。
    マルチノード構成において、全ノードへ同一のイベントを届ける役割を担います。
    """

    def __init__(self) -> None:
        """Redis クライアントを初期化します。"""
        self._redis: aioredis.Redis = aioredis.from_url(settings.REDIS_URL)

    async def publish(self, event: dict) -> None:
        """イベントを JSON 形式で Redis へパブリッシュします。

        Args:
            event (dict): 送信するイベントデータ。
        """
        await self._redis.publish(settings.REDIS_CHANNEL, json.dumps(event))


# シングルトンインスタンスとして公開
event_publisher = RedisEventPublisher()
