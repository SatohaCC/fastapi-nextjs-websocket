"""Outbox の未配信レコードを Redis へ Publish するバックグラウンドワーカー。"""

import asyncio
import json
import logging
import time

import asyncpg
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import async_sessionmaker

from ..config import settings
from ..persistence.sa_outbox_repository import SqlAlchemyDeliveryFeedRepository

logger = logging.getLogger(__name__)


async def relay_worker(session_factory: async_sessionmaker, redis_url: str) -> None:
    """未配信のフィードを定期的に取得し、Redis に送信するワーカー。"""
    redis = aioredis.from_url(redis_url)
    last_cleanup = time.time()
    wakeup_event = asyncio.Event()

    def _on_notify(conn, pid, channel, payload):
        """NOTIFYを受け取った際にイベントをセットし、メインループを起こす"""
        wakeup_event.set()

    # asyncpgは `postgresql+asyncpg://` プレフィックスを解釈しないため削除
    pg_url = settings.DATABASE_URL.replace("+asyncpg", "")

    async def listener_task():
        """バックグラウンドで LISTEN を維持し続けるタスク"""
        while True:
            conn = None
            try:
                conn = await asyncpg.connect(pg_url)
                await conn.add_listener("new_delivery_feed", _on_notify)
                logger.info("Started listening for 'new_delivery_feed' notifications")
                while not conn.is_closed():
                    await asyncio.sleep(1.0)
            except asyncio.CancelledError:
                if conn and not conn.is_closed():
                    await conn.close()
                break
            except Exception as e:
                logger.warning(f"Listener connection dropped: {e}")
                await asyncio.sleep(5.0)

    # リスナータスクをバックグラウンドで起動
    listener = asyncio.create_task(listener_task())

    try:
        while True:
            # ループの最初でイベントをクリアしておく。
            # これにより、処理中に発生した通知を確実にとらえられる（次の wait で即座に抜ける）。
            wakeup_event.clear()

            async with session_factory() as session:
                repo = SqlAlchemyDeliveryFeedRepository(session)

                # FOR UPDATE SKIP LOCKED で取得するため、他ワーカーと競合しない
                feeds = await repo.get_pending(limit=100)
                if feeds:
                    try:
                        for feed in feeds:
                            payload_to_publish = {
                                **feed.payload,
                                "seq": feed.sequence_id.value if feed.sequence_id else None,
                                "sequence_name": feed.sequence_name.value,
                            }
                            await redis.publish(
                                settings.REDIS_CHANNEL, json.dumps(payload_to_publish)
                            )

                        # 配信完了マーク
                        feed_keys = [
                            (f.sequence_name, f.sequence_id)
                            for f in feeds
                            if f.sequence_name and f.sequence_id is not None
                        ]
                        await repo.mark_processed(feed_keys)
                        await session.commit()

                        # 処理した場合は、まだ未処理のフィードがあるかもしれないので即座に次へループ
                        continue
                    except Exception:
                        logger.exception(
                            "Relay worker failed to publish feeds; will retry"
                        )
                        await session.rollback()

                # 1時間ごとにクリーンアップ処理を実行
                current_time = time.time()
                if current_time - last_cleanup > 3600:
                    try:
                        deleted = await repo.delete_old_processed_feeds(hours=24)
                        if deleted > 0:
                            logger.info(f"Cleaned up {deleted} old processed feeds")
                        await session.commit()
                    except Exception:
                        logger.exception("Failed to cleanup old feeds")
                        await session.rollback()
                    finally:
                        last_cleanup = current_time

            # フェッチしてもデータがなかった場合のみ、通知を待機する
            try:
                # 最大10秒待機（万が一通知を取りこぼした場合の保険ポーリング）
                await asyncio.wait_for(wakeup_event.wait(), timeout=10.0)
            except asyncio.TimeoutError:
                pass

    except asyncio.CancelledError:
        listener.cancel()
    finally:
        await redis.aclose()
