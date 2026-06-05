"""UserSettingsService のユニットテスト（UoW / Repository をモック化）。"""

from app.application.services.user_settings_service import UserSettingsService
from app.domain.entities.user_settings import UserSettings
from app.domain.primitives.primitives import Username


class TestUserSettingsServiceGetSettings:
    """UserSettingsService.get_settings のテスト。"""

    async def test_returns_default_settings_when_none_exists(self, mock_uow):
        """設定が登録されていない場合、デフォルト値を返すことを確認。

        DB には保存されないことを保証します。
        """
        mock_uow.user_settings.get.return_value = None
        service = UserSettingsService(mock_uow)

        username = Username("alice")
        result = await service.get_settings(username)

        assert result.username == username
        assert result.global_chat is True
        assert result.direct_request is True
        assert result.direct_request_updated is True
        mock_uow.user_settings.get.assert_called_once_with(username)
        mock_uow.user_settings.upsert.assert_not_called()
        mock_uow.commit.assert_not_called()

    async def test_returns_existing_settings(self, mock_uow):
        """既存の設定がある場合、それをそのまま返すことを確認します。"""
        username = Username("alice")
        existing = UserSettings(
            username=username,
            global_chat=False,
            direct_request=True,
            direct_request_updated=False,
        )
        mock_uow.user_settings.get.return_value = existing
        service = UserSettingsService(mock_uow)

        result = await service.get_settings(username)

        assert result == existing
        mock_uow.user_settings.get.assert_called_once_with(username)


class TestUserSettingsServiceUpdateSettings:
    """UserSettingsService.update_settings のテスト。"""

    async def test_upserts_settings_and_commits(self, mock_uow):
        """設定が upsert され、トランザクションがコミットされることを確認します。"""
        username = Username("bob")
        settings_to_save = UserSettings(
            username=username,
            global_chat=False,
            direct_request=False,
            direct_request_updated=True,
        )
        mock_uow.user_settings.upsert.return_value = settings_to_save
        service = UserSettingsService(mock_uow)

        result = await service.update_settings(
            username=username,
            global_chat=False,
            direct_request=False,
            direct_request_updated=True,
        )

        assert result == settings_to_save
        mock_uow.user_settings.upsert.assert_called_once()
        mock_uow.commit.assert_called_once()
