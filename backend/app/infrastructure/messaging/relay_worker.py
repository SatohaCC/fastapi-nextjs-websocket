"""Outbox の未配信レコードを Redis へ Publish するバックグラウンドワーカー。"""

import asyncio
import json
import logging
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager

import asyncpg
from redis import asyncio as aioredis

from ...application.uow import UnitOfWork
from ..config import settings
from ..serialization import feed_to_dict

logger = logging.getLogger(__name__)

UowFactory = Callable[[], AbstractAsyncContextManager[UnitOfWork]]


async def _listener_task(pg_url: str, wakeup_event: asyncio.Event) -> None:
    """バックグラウンドで PostgreSQL LISTEN を維持し続けるタスク。

    接続断が発生した場合は 5 秒待機後に自動再接続します。
    CancelledError は再送出して TaskGroup に伝播させます。
    """

    def _on_notify(conn: object, pid: int, channel: str, payload: str) -> None:
        wakeup_event.set()

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
            raise
        except Exception as e:
            logger.warning(f"Listener connection dropped: {e}")
            await asyncio.sleep(5.0)


async def _relay_loop(
    uow_factory: UowFactory,
    redis: aioredis.Redis,
    wakeup_event: asyncio.Event,
) -> None:
    """UoW を介して未配信フィードを取得し Redis へ中継するループ。

    フィードが存在する間は即座に次のイテレーションへ進み、
    フィードが空になった時点で NOTIFY か 10 秒タイムアウトまで待機します。
    """
    while True:
        # イベントをクリアしてから get_pending を呼ぶことで、
        # 処理中に届いた NOTIFY を取りこぼさない
        wakeup_event.clear()

        async with uow_factory() as uow:
            feeds = await uow.outbox.get_pending(limit=500)
            if feeds:
                try:
                    # pipeline で全件を 1 回の RTT にまとめて送信し、順序を保証する
                    async with redis.pipeline() as pipe:
                        for feed in feeds:
                            pipe.publish(
                                settings.REDIS_CHANNEL,
                                json.dumps(feed_to_dict(feed)),
                            )
                        await pipe.execute()

                    feed_keys = [
                        (f.sequence_name, f.sequence_id)
                        for f in feeds
                        if f.sequence_name and f.sequence_id is not None
                    ]
                    await uow.outbox.mark_processed(feed_keys)
                    await uow.commit()

                    # まだ未処理のフィードがある可能性があるため即座に再ループ
                    continue
                except Exception:
                    logger.exception("Relay worker failed to publish feeds; will retry")
                    await uow.rollback()

        # フィードが空、またはエラー発生時は通知か timeout まで待機
        try:
            await asyncio.wait_for(wakeup_event.wait(), timeout=10.0)
        except asyncio.TimeoutError:
            pass


async def relay_worker(uow_factory: UowFactory, redis_url: str) -> None:
    """未配信のフィードを定期的に取得し、Redis に送信するワーカー。

    asyncio.TaskGroup を使用してリスナータスクと中継ループを管理します。
    いずれかのタスクが予期せず失敗した場合、もう一方もキャンセルされます。
    """
    redis = aioredis.from_url(redis_url)
    wakeup_event = asyncio.Event()
    # asyncpg は `postgresql+asyncpg://` プレフィックスを解釈しないため削除
    pg_url = settings.DATABASE_URL.replace("+asyncpg", "")

    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(_listener_task(pg_url, wakeup_event))
            tg.create_task(_relay_loop(uow_factory, redis, wakeup_event))
    finally:
        await redis.aclose()
