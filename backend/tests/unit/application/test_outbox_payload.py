"""アプリケーション層 Payload クラスのユニットテスト。"""

from datetime import datetime, timezone

from app.application.outbox.payload import (
    GlobalChatPayload,
    RequestPayload,
    RequestUpdatePayload,
    SystemEventPayload,
)
from app.domain.primitives.feed import FeedEventType
from app.domain.primitives.primitives import (
    EntityId,
    MessageText,
    RequestText,
    Username,
)
from app.domain.primitives.request_status import RequestStatus


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


class TestRequestPayload:
    """RequestPayload のテスト。"""

    def test_event_type(self):
        """event_type が REQUEST であること。"""
        now = datetime.now(timezone.utc)
        payload = RequestPayload(
            id=EntityId(20),
            sender=Username("alice"),
            recipient=Username("bob"),
            text=RequestText("please review"),
            status=RequestStatus.REQUESTED,
            created_at=now,
            updated_at=now,
        )
        assert payload.event_type == FeedEventType.REQUEST

    def test_fields_are_stored(self):
        """指定したフィールドが正しく保持されること。"""
        now = datetime.now(timezone.utc)
        payload = RequestPayload(
            id=EntityId(20),
            sender=Username("alice"),
            recipient=Username("bob"),
            text=RequestText("please review"),
            status=RequestStatus.REQUESTED,
            created_at=now,
            updated_at=now,
        )
        assert payload.id == EntityId(20)
        assert payload.sender == Username("alice")
        assert payload.recipient == Username("bob")
        assert payload.status == RequestStatus.REQUESTED


class TestRequestUpdatePayload:
    """RequestUpdatePayload のテスト。"""

    def test_event_type(self):
        """event_type が REQUEST_UPDATED であること。"""
        payload = RequestUpdatePayload(
            id=EntityId(20),
            status=RequestStatus.PROCESSING,
            sender=Username("alice"),
            recipient=Username("bob"),
            updated_at=datetime.now(timezone.utc),
        )
        assert payload.event_type == FeedEventType.REQUEST_UPDATED

    def test_fields_are_stored(self):
        """指定したフィールドが正しく保持されること。"""
        payload = RequestUpdatePayload(
            id=EntityId(20),
            status=RequestStatus.PROCESSING,
            sender=Username("alice"),
            recipient=Username("bob"),
            updated_at=datetime.now(timezone.utc),
        )
        assert payload.id == EntityId(20)
        assert payload.status == RequestStatus.PROCESSING


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
