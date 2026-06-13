"""認証情報の保守を担うアプリケーションサービス。"""

import logging
from datetime import datetime, timezone

from ..uow import UnitOfWork

logger = logging.getLogger(__name__)


class AuthManagementService:
    """認証情報の保守（期限切れトークンのクリーンアップ等）を担うサービス。"""

    def __init__(self, uow: UnitOfWork) -> None:
        """サービスを初期化します。"""
        self._uow = uow

    async def cleanup_expired_tokens(self) -> int:
        """有効期限が切れたリフレッシュトークンを削除し、削除件数を返します。"""
        async with self._uow:
            now = datetime.now(timezone.utc)
            deleted = await self._uow.refresh_tokens.delete_expired(now)
            await self._uow.commit()
            return deleted
