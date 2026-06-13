"""AuthManagementService のユニットテスト（UoW をモック化）。"""

from unittest.mock import ANY

from app.application.services.auth_management_service import AuthManagementService


class TestAuthManagementServiceCleanupExpiredTokens:
    """AuthManagementService.cleanup_expired_tokens のテスト。"""

    async def test_calls_delete_expired_with_datetime(self, mock_uow):
        """delete_expired が datetime を引数にして呼ばれること。"""
        mock_uow.refresh_tokens.delete_expired.return_value = 5
        service = AuthManagementService(mock_uow)
        await service.cleanup_expired_tokens()
        mock_uow.refresh_tokens.delete_expired.assert_called_once_with(ANY)

    async def test_commits_transaction(self, mock_uow):
        """コミットが 1 回呼ばれること。"""
        mock_uow.refresh_tokens.delete_expired.return_value = 0
        service = AuthManagementService(mock_uow)
        await service.cleanup_expired_tokens()
        mock_uow.commit.assert_called_once()

    async def test_returns_deleted_count(self, mock_uow):
        """delete_expired の戻り値がそのまま返ること。"""
        mock_uow.refresh_tokens.delete_expired.return_value = 12
        service = AuthManagementService(mock_uow)
        result = await service.cleanup_expired_tokens()
        assert result == 12
