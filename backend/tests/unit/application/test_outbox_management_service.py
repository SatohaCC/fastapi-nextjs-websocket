"""OutboxManagementService のユニットテスト（UoW をモック化）。"""

from app.application.services.outbox_management_service import OutboxManagementService


class TestOutboxManagementServiceCleanupOldFeeds:
    """OutboxManagementService.cleanup_old_feeds のテスト。"""

    async def test_calls_delete_with_correct_hours(self, mock_uow):
        """delete_old_processed_feeds が正しい hours 引数で呼ばれること。"""
        mock_uow.outbox.delete_old_processed_feeds.return_value = 3
        service = OutboxManagementService(mock_uow)
        await service.cleanup_old_feeds(hours=48)
        mock_uow.outbox.delete_old_processed_feeds.assert_called_once_with(hours=48)

    async def test_uses_default_hours_24(self, mock_uow):
        """デフォルト hours=24 で delete_old_processed_feeds が呼ばれること。"""
        mock_uow.outbox.delete_old_processed_feeds.return_value = 0
        service = OutboxManagementService(mock_uow)
        await service.cleanup_old_feeds()
        mock_uow.outbox.delete_old_processed_feeds.assert_called_once_with(hours=24)

    async def test_commits_transaction(self, mock_uow):
        """コミットが 1 回呼ばれること。"""
        mock_uow.outbox.delete_old_processed_feeds.return_value = 0
        service = OutboxManagementService(mock_uow)
        await service.cleanup_old_feeds()
        mock_uow.commit.assert_called_once()

    async def test_returns_deleted_count(self, mock_uow):
        """delete_old_processed_feeds の戻り値がそのまま返ること。"""
        mock_uow.outbox.delete_old_processed_feeds.return_value = 7
        service = OutboxManagementService(mock_uow)
        result = await service.cleanup_old_feeds()
        assert result == 7

    async def test_returns_zero_when_nothing_deleted(self, mock_uow):
        """削除対象がない場合は 0 を返すこと。"""
        mock_uow.outbox.delete_old_processed_feeds.return_value = 0
        service = OutboxManagementService(mock_uow)
        result = await service.cleanup_old_feeds()
        assert result == 0
