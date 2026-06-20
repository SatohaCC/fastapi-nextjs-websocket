"""ユーザー通知設定のリポジトリインターフェース。"""

from typing import Protocol

from app.domain.entities.user_settings import UserSettings
from app.domain.primitives.primitives import UserId


class UserSettingsRepository(Protocol):
    """ユーザー通知設定の参照および更新を行うリポジトリ。"""

    async def get(self, user_id: UserId) -> UserSettings | None:
        """指定されたユーザー ID に対応する通知設定を取得します。

        設定が存在しない場合は None を返します。
        """
        ...

    async def upsert(self, settings: UserSettings) -> UserSettings:
        """指定された通知設定を保存または更新（Upsert）します。"""
        ...
