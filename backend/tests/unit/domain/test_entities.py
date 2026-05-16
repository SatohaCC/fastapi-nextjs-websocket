"""Task エンティティのステータス遷移・権限チェックのユニットテスト。"""

from datetime import datetime, timezone

import pytest

from app.domain.entities.task import DraftTask, Task
from app.domain.exceptions import (
    DomainValidationError,
    InvalidOperationException,
    UnauthorizedException,
)
from app.domain.primitives.primitives import EntityId, TaskText, Username
from app.domain.primitives.task_status import TaskStatus


def make_task(
    sender: str = "alice",
    recipient: str = "bob",
    status: TaskStatus = TaskStatus.REQUESTED,
) -> Task:
    """テスト用 Task を生成するヘルパー。"""
    now = datetime.now(timezone.utc)
    return Task(
        id=EntityId(1),
        sender=Username(sender),
        recipient=Username(recipient),
        text=TaskText("please help"),
        status=status,
        created_at=now,
        updated_at=now,
    )


class TestDraftTask:
    """DraftTask の不変条件テスト。"""

    def test_self_request_raises(self):
        """送信者と受信者が同じ場合は DomainValidationError を送出する。"""
        with pytest.raises(DomainValidationError):
            DraftTask(
                sender=Username("alice"),
                recipient=Username("alice"),
                text=TaskText("test"),
                status=TaskStatus.REQUESTED,
            )

    def test_different_sender_recipient_is_valid(self):
        """送信者と受信者が異なる場合は有効。"""
        DraftTask(
            sender=Username("alice"),
            recipient=Username("bob"),
            text=TaskText("test"),
            status=TaskStatus.REQUESTED,
        )


class TestTaskTransition:
    """Task.transition_to のテスト。"""

    def test_valid_transition_updates_status(self):
        """受信者による有効な遷移でステータスが更新される。"""
        task = make_task()
        updated = task.transition_to(TaskStatus.PROCESSING, Username("bob"))
        assert updated.status == TaskStatus.PROCESSING

    def test_valid_transition_updates_timestamp(self):
        """有効な遷移後に updated_at が更新される（元の値以上）。"""
        task = make_task()
        updated = task.transition_to(TaskStatus.PROCESSING, Username("bob"))
        assert updated.updated_at >= task.updated_at

    def test_non_recipient_raises_unauthorized(self):
        """受信者以外が操作すると UnauthorizedException を送出する。"""
        task = make_task()
        with pytest.raises(UnauthorizedException):
            task.transition_to(TaskStatus.PROCESSING, Username("alice"))

    def test_invalid_transition_raises(self):
        """無効なステータス遷移は InvalidOperationException を送出する。"""
        task = make_task(status=TaskStatus.COMPLETED)
        with pytest.raises(InvalidOperationException):
            task.transition_to(TaskStatus.REQUESTED, Username("bob"))

    def test_chained_valid_transitions(self):
        """REQUESTED → PROCESSING → COMPLETED の連続遷移が成功する。"""
        task = make_task()
        processing = task.transition_to(TaskStatus.PROCESSING, Username("bob"))
        completed = processing.transition_to(TaskStatus.COMPLETED, Username("bob"))
        assert completed.status == TaskStatus.COMPLETED

    def test_transition_returns_new_instance(self):
        """transition_to は元のインスタンスを変更せず新しいインスタンスを返す。

        不変性の検証。
        """
        task = make_task()
        updated = task.transition_to(TaskStatus.PROCESSING, Username("bob"))
        assert task.status == TaskStatus.REQUESTED
        assert updated.status == TaskStatus.PROCESSING
        assert task is not updated
