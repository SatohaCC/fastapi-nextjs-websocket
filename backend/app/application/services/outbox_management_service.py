"""Outbox テーブルの保守を担うアプリケーションサービス。"""

import logging

from ..uow import UnitOfWork

logger = logging.getLogger(__name__)


class OutboxManagementService:
    """Outbox テーブルの保守（古いレコードのクリーンアップ等）を担うサービス。"""

    def __init__(self, uow: UnitOfWork) -> None:
        """サービスを初期化します。"""
        self._uow = uow

    async def cleanup_old_feeds(self, hours: int = 24) -> int:
        """指定時間以上経過した処理済みフィードを削除し、削除件数を返します。"""
        async with self._uow:
            deleted = await self._uow.outbox.delete_old_processed_feeds(hours=hours)
            await self._uow.commit()
            return deleted
