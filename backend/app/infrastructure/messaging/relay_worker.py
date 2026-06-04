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
        print(
            f"[RELAY_WORKER] NOTIFY received on channel {channel} "
            f"with payload {payload}",
            flush=True,
        )
        wakeup_event.set()

    while True:
        conn = None
        try:
            conn = await asyncpg.connect(pg_url)
            await conn.add_listener("new_delivery_feed", _on_notify)
            print(
                "[RELAY_WORKER] Started listening for "
                "'new_delivery_feed' notifications",
                flush=True,
            )
            logger.info("Started listening for 'new_delivery_feed' notifications")
            while not conn.is_closed():
                await asyncio.sleep(1.0)
        except asyncio.CancelledError:
            if conn and not conn.is_closed():
                await conn.close()
            raise
        except Exception as e:
            print(f"[RELAY_WORKER] Listener connection dropped: {e}", flush=True)
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
                print(
                    f"[RELAY_WORKER] Found {len(feeds)} pending feeds. Processing...",
                    flush=True,
                )
                try:
                    # pipeline で全件を 1 回の RTT にまとめて送信し、順序を保証する
                    async with redis.pipeline() as pipe:
                        for feed in feeds:
                            print(
                                f"[RELAY_WORKER] Publishing feed "
                                f"{feed.sequence_id} (event: {feed.event_type}) "
                                "to Redis",
                                flush=True,
                            )
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
                    print(
                        f"[RELAY_WORKER] Marked {len(feeds)} feeds as processed.",
                        flush=True,
                    )

                    # まだ未処理のフィードがある可能性があるため即座に再ループ
                    continue
                except Exception as e:
                    print(
                        f"[RELAY_WORKER] Exception in relay loop processing: {e}",
                        flush=True,
                    )
                    logger.exception("Relay worker failed to publish feeds; will retry")
                    await uow.rollback()

        # フィードが空、またはエラー発生時は通知か timeout まで待機
        try:
            print(
                "[RELAY_WORKER] Waiting for wakeup notification or timeout...",
                flush=True,
            )
            await asyncio.wait_for(wakeup_event.wait(), timeout=10.0)
            print("[RELAY_WORKER] Woke up by notification!", flush=True)
        except asyncio.TimeoutError:
            print("[RELAY_WORKER] Woke up by timeout (10s)", flush=True)
            pass


async def relay_worker(uow_factory: UowFactory, redis_url: str) -> None:
    """未配信のフィードを定期的に取得し、Redis に送信するワーカー。

    asyncio.TaskGroup を使用してリスナータスクと中継ループを管理します。
    いずれかのタスクが予期せず失敗した場合、もう一方もキャンセルされ、再起動します。
    """
    pg_url = settings.DATABASE_URL.replace("+asyncpg", "")

    while True:
        redis = None
        try:
            print("[RELAY_WORKER] Starting relay_worker tasks...", flush=True)
            redis = aioredis.from_url(
                redis_url,
                socket_timeout=None,
                socket_keepalive=True,
                health_check_interval=30,
            )
            wakeup_event = asyncio.Event()
            async with asyncio.TaskGroup() as tg:
                tg.create_task(_listener_task(pg_url, wakeup_event))
                tg.create_task(_relay_loop(uow_factory, redis, wakeup_event))
        except asyncio.CancelledError:
            print("[RELAY_WORKER] relay_worker task cancelled.", flush=True)
            raise
        except Exception as e:
            print(
                f"[RELAY_WORKER] Exception in relay_worker: {e}. Restarting in 5s...",
                flush=True,
            )
            await asyncio.sleep(5.0)
        finally:
            if redis is not None:
                try:
                    await redis.aclose()
                except Exception:
                    pass
