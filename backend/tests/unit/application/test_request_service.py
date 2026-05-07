"""RequestService のユニットテスト（UoW / Repository をモック化）。"""

from datetime import datetime, timezone

import pytest

from app.application.services.request_service import RequestService
from app.domain.entities.direct_request import DirectRequest
from app.domain.exceptions import EntityNotFoundException
from app.domain.primitives.primitives import EntityId, RequestText, Username
from app.domain.primitives.request_status import RequestStatus


@pytest.fixture
def saved_request() -> DirectRequest:
    """テスト用の永続化済み DirectRequest（REQUESTED 状態）。"""
    now = datetime.now(timezone.utc)
    return DirectRequest(
        id=EntityId(1),
        sender=Username("alice"),
        recipient=Username("bob"),
        text=RequestText("please review"),
        status=RequestStatus.REQUESTED,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def processing_request(saved_request) -> DirectRequest:
    """PROCESSING 状態の DirectRequest。"""
    return saved_request.transition_to(RequestStatus.PROCESSING, Username("bob"))


class TestRequestServiceSendRequest:
    """RequestService.send_request のテスト。"""

    async def test_saves_request_to_repository(self, mock_uow, saved_request):
        """requests.save が 1 回呼ばれること。"""
        mock_uow.requests.save.return_value = saved_request
        service = RequestService(mock_uow)
        await service.send_request(
            Username("alice"), Username("bob"), RequestText("please review")
        )
        mock_uow.requests.save.assert_called_once()

    async def test_saves_feed_to_outbox(self, mock_uow, saved_request):
        """outbox.save が 1 回呼ばれること（Transactional Outbox）。"""
        mock_uow.requests.save.return_value = saved_request
        service = RequestService(mock_uow)
        await service.send_request(
            Username("alice"), Username("bob"), RequestText("please review")
        )
        mock_uow.outbox.save.assert_called_once()

    async def test_commits_transaction(self, mock_uow, saved_request):
        """Commit が 1 回呼ばれること。"""
        mock_uow.requests.save.return_value = saved_request
        service = RequestService(mock_uow)
        await service.send_request(
            Username("alice"), Username("bob"), RequestText("please review")
        )
        mock_uow.commit.assert_called_once()

    async def test_returns_saved_request(self, mock_uow, saved_request):
        """requests.save の戻り値がそのまま返ること。"""
        mock_uow.requests.save.return_value = saved_request
        service = RequestService(mock_uow)
        result = await service.send_request(
            Username("alice"), Username("bob"), RequestText("please review")
        )
        assert result == saved_request


class TestRequestServiceUpdateStatus:
    """RequestService.update_status のテスト。"""

    async def test_fetches_request_by_id(
        self, mock_uow, saved_request, processing_request
    ):
        """requests.get_by_id が指定した request_id で呼ばれること。"""
        mock_uow.requests.get_by_id.return_value = saved_request
        mock_uow.requests.save.return_value = processing_request
        service = RequestService(mock_uow)
        await service.update_status(
            EntityId(1), RequestStatus.PROCESSING, Username("bob")
        )
        mock_uow.requests.get_by_id.assert_called_once_with(EntityId(1))

    async def test_saves_transitioned_request(
        self, mock_uow, saved_request, processing_request
    ):
        """遷移後のリクエストが requests.save で保存されること。"""
        mock_uow.requests.get_by_id.return_value = saved_request
        mock_uow.requests.save.return_value = processing_request
        service = RequestService(mock_uow)
        await service.update_status(
            EntityId(1), RequestStatus.PROCESSING, Username("bob")
        )
        mock_uow.requests.save.assert_called_once()

    async def test_saves_update_feed_to_outbox(
        self, mock_uow, saved_request, processing_request
    ):
        """ステータス更新フィードが outbox.save で記録されること。"""
        mock_uow.requests.get_by_id.return_value = saved_request
        mock_uow.requests.save.return_value = processing_request
        service = RequestService(mock_uow)
        await service.update_status(
            EntityId(1), RequestStatus.PROCESSING, Username("bob")
        )
        mock_uow.outbox.save.assert_called_once()

    async def test_commits_transaction(
        self, mock_uow, saved_request, processing_request
    ):
        """Commit が 1 回呼ばれること。"""
        mock_uow.requests.get_by_id.return_value = saved_request
        mock_uow.requests.save.return_value = processing_request
        service = RequestService(mock_uow)
        await service.update_status(
            EntityId(1), RequestStatus.PROCESSING, Username("bob")
        )
        mock_uow.commit.assert_called_once()

    async def test_not_found_raises_entity_not_found(self, mock_uow):
        """リクエストが存在しない場合は EntityNotFoundException を送出すること。"""
        mock_uow.requests.get_by_id.return_value = None
        service = RequestService(mock_uow)
        with pytest.raises(EntityNotFoundException):
            await service.update_status(
                EntityId(999), RequestStatus.PROCESSING, Username("bob")
            )

    async def test_returns_updated_request(
        self, mock_uow, saved_request, processing_request
    ):
        """更新後のリクエストが返ること。"""
        mock_uow.requests.get_by_id.return_value = saved_request
        mock_uow.requests.save.return_value = processing_request
        service = RequestService(mock_uow)
        result = await service.update_status(
            EntityId(1), RequestStatus.PROCESSING, Username("bob")
        )
        assert result == processing_request


class TestRequestServiceGetRequests:
    """RequestService の読み取りメソッドのテスト。"""

    async def test_get_requests_for_user_delegates_to_repository(self, mock_uow):
        """get_requests_for_user が requests.get_for_user を正しい引数で呼ぶこと。"""
        mock_uow.requests.get_for_user.return_value = []
        service = RequestService(mock_uow)
        result = await service.get_requests_for_user(Username("alice"))
        mock_uow.requests.get_for_user.assert_called_once_with(Username("alice"))
        assert result == []

    async def test_get_requests_after_delegates_to_repository(self, mock_uow):
        """get_requests_after が requests.get_after を正しい引数で呼ぶこと。"""
        mock_uow.requests.get_after.return_value = []
        service = RequestService(mock_uow)
        result = await service.get_requests_after(Username("alice"), EntityId(5))
        mock_uow.requests.get_after.assert_called_once_with(
            Username("alice"), EntityId(5)
        )
        assert result == []
