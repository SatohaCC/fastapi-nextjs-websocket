"""ユーザー通知設定のビジネスロジックを管理するアプリケーションサービス。"""

from app.application.uow import UnitOfWork
from app.domain.entities.user_settings import UserSettings
from app.domain.primitives.primitives import UserId


class UserSettingsService:
    """ユーザー通知設定の管理を行うサービス。"""

    def __init__(self, uow: UnitOfWork):
        """Service を初期化します。"""
        self._uow = uow

    async def get_settings(self, user_id: UserId) -> UserSettings:
        """指定されたユーザー ID に対応する通知設定を取得します。

        DB に設定行が存在しない場合は、デフォルト設定を返します。
        （DB への新規保存は行いません）
        """
        async with self._uow as uow:
            settings = await uow.user_settings.get(user_id)
            if settings is None:
                return UserSettings(
                    user_id=user_id,
                    global_chat=True,
                    direct_request=True,
                    direct_request_updated=True,
                )
            return settings

    async def update_settings(
        self,
        user_id: UserId,
        global_chat: bool,
        direct_request: bool,
        direct_request_updated: bool,
    ) -> UserSettings:
        """指定されたユーザーの通知設定を新規作成または更新します。"""
        async with self._uow as uow:
            settings = UserSettings(
                user_id=user_id,
                global_chat=global_chat,
                direct_request=direct_request,
                direct_request_updated=direct_request_updated,
            )
            updated = await uow.user_settings.upsert(settings)
            await self._uow.commit()
            return updated
