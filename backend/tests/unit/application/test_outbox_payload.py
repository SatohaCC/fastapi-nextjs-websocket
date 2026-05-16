"""アプリケーション層 Payload クラスのユニットテスト。"""

from datetime import datetime, timezone

from app.application.outbox.payload import (
    DirectRequestPayload,
    DirectRequestUpdatePayload,
    GlobalChatPayload,
    SystemEventPayload,
)
from app.domain.primitives.feed import FeedEventType
from app.domain.primitives.primitives import (
    EntityId,
    MessageText,
    TaskText,
    Username,
)
from app.domain.primitives.task_status import TaskStatus


class TestGlobalChatPayload:
    """GlobalChatPayload のテスト。"""

    def test_event_type(self):
        """event_type が GLOBAL_CHAT であること。"""
        payload = GlobalChatPayload(
            id=EntityId(10),
            username=Username("alice"),
            text=MessageText("hello"),
            created_at=datetime.now(timezone.utc),
        )
        assert payload.event_type == FeedEventType.GLOBAL_CHAT

    def test_fields_are_stored(self):
        """指定したフィールドが正しく保持されること。"""
        now = datetime.now(timezone.utc)
        payload = GlobalChatPayload(
            id=EntityId(10),
            username=Username("alice"),
            text=MessageText("hello"),
            created_at=now,
        )
        assert payload.id == EntityId(10)
        assert payload.username == Username("alice")
        assert payload.text == MessageText("hello")
        assert payload.created_at == now


class TestDirectRequestPayload:
    """DirectRequestPayload のテスト。"""

    def test_event_type(self):
        """event_type が DIRECT_REQUEST であること。"""
        now = datetime.now(timezone.utc)
        payload = DirectRequestPayload(
            id=EntityId(20),
            sender=Username("alice"),
            recipient=Username("bob"),
            text=TaskText("please review"),
            status=TaskStatus.REQUESTED,
            created_at=now,
            updated_at=now,
        )
        assert payload.event_type == FeedEventType.DIRECT_REQUEST

    def test_fields_are_stored(self):
        """指定したフィールドが正しく保持されること。"""
        now = datetime.now(timezone.utc)
        payload = DirectRequestPayload(
            id=EntityId(20),
            sender=Username("alice"),
            recipient=Username("bob"),
            text=TaskText("please review"),
            status=TaskStatus.REQUESTED,
            created_at=now,
            updated_at=now,
        )
        assert payload.id == EntityId(20)
        assert payload.sender == Username("alice")
        assert payload.recipient == Username("bob")
        assert payload.status == TaskStatus.REQUESTED


class TestDirectRequestUpdatePayload:
    """DirectRequestUpdatePayload のテスト。"""

    def test_event_type(self):
        """event_type が DIRECT_REQUEST_UPDATED であること。"""
        payload = DirectRequestUpdatePayload(
            id=EntityId(20),
            status=TaskStatus.PROCESSING,
            sender=Username("alice"),
            recipient=Username("bob"),
            updated_at=datetime.now(timezone.utc),
        )
        assert payload.event_type == FeedEventType.DIRECT_REQUEST_UPDATED

    def test_fields_are_stored(self):
        """指定したフィールドが正しく保持されること。"""
        payload = DirectRequestUpdatePayload(
            id=EntityId(20),
            status=TaskStatus.PROCESSING,
            sender=Username("alice"),
            recipient=Username("bob"),
            updated_at=datetime.now(timezone.utc),
        )
        assert payload.id == EntityId(20)
        assert payload.status == TaskStatus.PROCESSING


class TestSystemEventPayload:
    """SystemEventPayload のテスト。"""

    def test_join_event_type(self):
        """JOIN イベントの event_type が正しいこと。"""
        payload = SystemEventPayload(
            type=FeedEventType.JOIN, username=Username("alice")
        )
        assert payload.event_type == FeedEventType.JOIN
        assert payload.username == Username("alice")

    def test_leave_event_type(self):
        """LEAVE イベントの event_type が正しいこと。"""
        payload = SystemEventPayload(type=FeedEventType.LEAVE, username=Username("bob"))
        assert payload.event_type == FeedEventType.LEAVE
        assert payload.username == Username("bob")
