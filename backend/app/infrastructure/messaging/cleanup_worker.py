"""Outbox の古い処理済みレコードを定期的に削除するバックグラウンドワーカー。"""

import asyncio
import logging
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager

from ...application.services.auth_management_service import AuthManagementService
from ...application.services.outbox_management_service import OutboxManagementService
from ...application.uow import UnitOfWork

logger = logging.getLogger(__name__)

UowFactory = Callable[[], AbstractAsyncContextManager[UnitOfWork]]


async def cleanup_worker(
    uow_factory: UowFactory,
    interval_seconds: int = 3600,
) -> None:
    """処理済みの古いフィードを定期的にクリーンアップするワーカー。

    起動直後は interval_seconds 待機してから初回クリーンアップを実行します。
    イテレーションごとに新しい UoW（セッション）を作成するため、
    長時間のセッション保持が発生しません。
    """
    while True:
        try:
            await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            return

        try:
            async with uow_factory() as uow:
                service = OutboxManagementService(uow)
                deleted = await service.cleanup_old_feeds(hours=24)
                if deleted > 0:
                    logger.info(f"Cleaned up {deleted} old processed feeds")

                auth_service = AuthManagementService(uow)
                deleted_tokens = await auth_service.cleanup_expired_tokens()
                if deleted_tokens > 0:
                    logger.info(f"Cleaned up {deleted_tokens} expired refresh tokens")
        except asyncio.CancelledError:
            return
        except Exception:
            logger.exception("Failed to cleanup old feeds")
