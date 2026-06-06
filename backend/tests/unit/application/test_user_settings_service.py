"""UserSettingsService のユニットテスト（UoW / Repository をモック化）。"""

import uuid

from app.application.services.user_settings_service import UserSettingsService
from app.domain.entities.user_settings import UserSettings
from app.domain.primitives.primitives import UserId

ALICE_ID = UserId(uuid.uuid7())
BOB_ID = UserId(uuid.uuid7())


class TestUserSettingsServiceGetSettings:
    """UserSettingsService.get_settings のテスト。"""

    async def test_returns_default_settings_when_none_exists(self, mock_uow):
        """設定が登録されていない場合、デフォルト値を返すことを確認。

        DB には保存されないことを保証します。
        """
        mock_uow.user_settings.get.return_value = None
        service = UserSettingsService(mock_uow)

        result = await service.get_settings(ALICE_ID)

        assert result.user_id == ALICE_ID
        assert result.global_chat is True
        assert result.direct_request is True
        assert result.direct_request_updated is True
        assert result.browser_notification is False
        mock_uow.user_settings.get.assert_called_once_with(ALICE_ID)
        mock_uow.user_settings.upsert.assert_not_called()
        mock_uow.commit.assert_not_called()

    async def test_returns_existing_settings(self, mock_uow):
        """既存の設定がある場合、それをそのまま返すことを確認します。"""
        existing = UserSettings(
            user_id=ALICE_ID,
            global_chat=False,
            direct_request=True,
            direct_request_updated=False,
            browser_notification=True,
        )
        mock_uow.user_settings.get.return_value = existing
        service = UserSettingsService(mock_uow)

        result = await service.get_settings(ALICE_ID)

        assert result == existing
        mock_uow.user_settings.get.assert_called_once_with(ALICE_ID)


class TestUserSettingsServiceUpdateSettings:
    """UserSettingsService.update_settings のテスト。"""

    async def test_upserts_settings_and_commits(self, mock_uow):
        """設定が upsert され、トランザクションがコミットされることを確認します。"""
        settings_to_save = UserSettings(
            user_id=BOB_ID,
            global_chat=False,
            direct_request=False,
            direct_request_updated=True,
            browser_notification=True,
        )
        mock_uow.user_settings.upsert.return_value = settings_to_save
        service = UserSettingsService(mock_uow)

        result = await service.update_settings(
            user_id=BOB_ID,
            global_chat=False,
            direct_request=False,
            direct_request_updated=True,
            browser_notification=True,
        )

        assert result == settings_to_save
        mock_uow.user_settings.upsert.assert_called_once()
        mock_uow.commit.assert_called_once()
