"""DirectRequestService のユニットテスト（UoW / Repository をモック化）。"""

from datetime import datetime, timezone

import pytest

from app.application.outbox.delivery_feed import DIRECT_REQUEST_SEQUENCE
from app.application.outbox.payload import (
    DirectRequestPayload,
    DirectRequestUpdatePayload,
)
from app.application.services.direct_request_service import DirectRequestService
from app.domain.entities.task import Task
from app.domain.exceptions import EntityNotFoundException
from app.domain.primitives.primitives import EntityId, TaskText, Username
from app.domain.primitives.task_status import TaskStatus


@pytest.fixture
def saved_task() -> Task:
    """テスト用の永続化済み Task（REQUESTED 状態）。"""
    now = datetime.now(timezone.utc)
    return Task(
        id=EntityId(1),
        sender=Username("alice"),
        recipient=Username("bob"),
        text=TaskText("please review"),
        status=TaskStatus.REQUESTED,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def processing_task(saved_task) -> Task:
    """PROCESSING 状態の Task。"""
    return saved_task.transition_to(TaskStatus.PROCESSING, Username("bob"))


class TestDirectRequestServiceSendRequest:
    """DirectRequestService.send_request のテスト。"""

    async def test_saves_task_to_repository(self, mock_uow, saved_task):
        """tasks.save が 1 回呼ばれること。"""
        mock_uow.tasks.save.return_value = saved_task
        service = DirectRequestService(mock_uow)
        await service.send_request(
            Username("alice"), Username("bob"), TaskText("please review")
        )
        mock_uow.tasks.save.assert_called_once()

    async def test_saves_feed_to_outbox(self, mock_uow, saved_task):
        """outbox.save が 1 回呼ばれること（Transactional Outbox）。"""
        mock_uow.tasks.save.return_value = saved_task
        service = DirectRequestService(mock_uow)
        await service.send_request(
            Username("alice"), Username("bob"), TaskText("please review")
        )
        mock_uow.outbox.save.assert_called_once()

    async def test_commits_transaction(self, mock_uow, saved_task):
        """Commit が 1 回呼ばれること。"""
        mock_uow.tasks.save.return_value = saved_task
        service = DirectRequestService(mock_uow)
        await service.send_request(
            Username("alice"), Username("bob"), TaskText("please review")
        )
        mock_uow.commit.assert_called_once()

    async def test_returns_saved_task(self, mock_uow, saved_task):
        """tasks.save の戻り値がそのまま返ること。"""
        mock_uow.tasks.save.return_value = saved_task
        service = DirectRequestService(mock_uow)
        result = await service.send_request(
            Username("alice"), Username("bob"), TaskText("please review")
        )
        assert result == saved_task

    async def test_outbox_feed_payload_maps_entity_fields(self, mock_uow, saved_task):
        """Outbox の DirectRequestPayload が entity フィールドと一致すること。"""
        mock_uow.tasks.save.return_value = saved_task
        service = DirectRequestService(mock_uow)
        await service.send_request(
            Username("alice"), Username("bob"), TaskText("please review")
        )

        feed = mock_uow.outbox.save.call_args.args[0]
        assert isinstance(feed.payload, DirectRequestPayload)
        assert feed.payload.id == saved_task.id
        assert feed.payload.sender == saved_task.sender
        assert feed.payload.recipient == saved_task.recipient
        assert feed.payload.text == saved_task.text
        assert feed.payload.status == saved_task.status

    async def test_outbox_feed_uses_direct_request_sequence(self, mock_uow, saved_task):
        """Outbox フィードのシーケンス名が DIRECT_REQUEST_SEQUENCE であること。"""
        mock_uow.tasks.save.return_value = saved_task
        service = DirectRequestService(mock_uow)
        await service.send_request(
            Username("alice"), Username("bob"), TaskText("please review")
        )

        feed = mock_uow.outbox.save.call_args.args[0]
        assert feed.sequence_name == DIRECT_REQUEST_SEQUENCE


class TestDirectRequestServiceUpdateStatus:
    """DirectRequestService.update_status のテスト。"""

    async def test_fetches_task_by_id(self, mock_uow, saved_task, processing_task):
        """tasks.get_by_id が指定した task_id で呼ばれること。"""
        mock_uow.tasks.get_by_id.return_value = saved_task
        mock_uow.tasks.save.return_value = processing_task
        service = DirectRequestService(mock_uow)
        await service.update_status(EntityId(1), TaskStatus.PROCESSING, Username("bob"))
        mock_uow.tasks.get_by_id.assert_called_once_with(EntityId(1))

    async def test_saves_transitioned_task(self, mock_uow, saved_task, processing_task):
        """遷移後の Task が tasks.save で保存されること。"""
        mock_uow.tasks.get_by_id.return_value = saved_task
        mock_uow.tasks.save.return_value = processing_task
        service = DirectRequestService(mock_uow)
        await service.update_status(EntityId(1), TaskStatus.PROCESSING, Username("bob"))
        mock_uow.tasks.save.assert_called_once()

    async def test_saves_update_feed_to_outbox(
        self, mock_uow, saved_task, processing_task
    ):
        """ステータス更新フィードが outbox.save で記録されること。"""
        mock_uow.tasks.get_by_id.return_value = saved_task
        mock_uow.tasks.save.return_value = processing_task
        service = DirectRequestService(mock_uow)
        await service.update_status(EntityId(1), TaskStatus.PROCESSING, Username("bob"))
        mock_uow.outbox.save.assert_called_once()

    async def test_commits_transaction(self, mock_uow, saved_task, processing_task):
        """Commit が 1 回呼ばれること。"""
        mock_uow.tasks.get_by_id.return_value = saved_task
        mock_uow.tasks.save.return_value = processing_task
        service = DirectRequestService(mock_uow)
        await service.update_status(EntityId(1), TaskStatus.PROCESSING, Username("bob"))
        mock_uow.commit.assert_called_once()

    async def test_not_found_raises_entity_not_found(self, mock_uow):
        """Task が存在しない場合は EntityNotFoundException を送出すること。"""
        mock_uow.tasks.get_by_id.return_value = None
        service = DirectRequestService(mock_uow)
        with pytest.raises(EntityNotFoundException):
            await service.update_status(
                EntityId(999), TaskStatus.PROCESSING, Username("bob")
            )

    async def test_returns_updated_task(self, mock_uow, saved_task, processing_task):
        """更新後の Task が返ること。"""
        mock_uow.tasks.get_by_id.return_value = saved_task
        mock_uow.tasks.save.return_value = processing_task
        service = DirectRequestService(mock_uow)
        result = await service.update_status(
            EntityId(1), TaskStatus.PROCESSING, Username("bob")
        )
        assert result == processing_task

    async def test_outbox_feed_payload_maps_updated_entity_fields(
        self, mock_uow, saved_task, processing_task
    ):
        """update_status の outbox フィードの Payload が entity と一致すること。"""
        mock_uow.tasks.get_by_id.return_value = saved_task
        mock_uow.tasks.save.return_value = processing_task
        service = DirectRequestService(mock_uow)
        await service.update_status(EntityId(1), TaskStatus.PROCESSING, Username("bob"))

        feed = mock_uow.outbox.save.call_args.args[0]
        assert isinstance(feed.payload, DirectRequestUpdatePayload)
        assert feed.payload.id == processing_task.id
        assert feed.payload.status == processing_task.status
        assert feed.payload.sender == processing_task.sender
        assert feed.payload.recipient == processing_task.recipient


class TestDirectRequestServiceGetTasks:
    """DirectRequestService の読み取りメソッドのテスト。"""

    async def test_get_tasks_for_user_delegates_to_repository(self, mock_uow):
        """get_tasks_for_user が tasks.get_for_user を正しい引数で呼ぶこと。"""
        mock_uow.tasks.get_for_user.return_value = []
        service = DirectRequestService(mock_uow)
        result = await service.get_tasks_for_user(Username("alice"))
        mock_uow.tasks.get_for_user.assert_called_once_with(Username("alice"))
        assert result == []

    async def test_get_tasks_after_delegates_to_repository(self, mock_uow):
        """get_tasks_after が tasks.get_after を正しい引数で呼ぶこと。"""
        mock_uow.tasks.get_after.return_value = []
        service = DirectRequestService(mock_uow)
        result = await service.get_tasks_after(Username("alice"), EntityId(5))
        mock_uow.tasks.get_after.assert_called_once_with(Username("alice"), EntityId(5))
        assert result == []
