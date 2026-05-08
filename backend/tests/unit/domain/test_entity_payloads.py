"""ドメインエンティティの Payload 生成メソッドのユニットテスト。"""

from datetime import datetime, timezone

import pytest

from app.domain.entities.direct_request import DirectRequest
from app.domain.entities.message import Message
from app.domain.entities.payload import (
    MessagePayload,
    RequestPayload,
    RequestUpdatePayload,
    SystemEventPayload,
)
from app.domain.entities.system_event import SystemEvent
from app.domain.primitives.feed import FeedEventType
from app.domain.primitives.primitives import (
    EntityId,
    MessageText,
    RequestText,
    Username,
)
from app.domain.primitives.request_status import RequestStatus


@pytest.fixture
def sample_message() -> Message:
    """テスト用 Message エンティティ。"""
    return Message(
        id=EntityId(10),
        username=Username("alice"),
        text=MessageText("hello world"),
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_request() -> DirectRequest:
    """テスト用 DirectRequest エンティティ。"""
    now = datetime.now(timezone.utc)
    return DirectRequest(
        id=EntityId(20),
        sender=Username("alice"),
        recipient=Username("bob"),
        text=RequestText("please review"),
        status=RequestStatus.REQUESTED,
        created_at=now,
        updated_at=now,
    )


class TestMessagePayload:
    """Message.to_payload のテスト。"""

    def test_to_payload_returns_correct_type(self, sample_message):
        """正しい Payload 型と event_type が取得できること。"""
        payload = sample_message.to_payload()
        assert isinstance(payload, MessagePayload)
        assert payload.event_type == FeedEventType.MESSAGE

    def test_payload_fields_match_entity(self, sample_message):
        """Payload のフィールドが元のエンティティと一致すること。"""
        payload = sample_message.to_payload()
        assert payload.id == sample_message.id
        assert payload.username == sample_message.username
        assert payload.text == sample_message.text
        assert payload.created_at == sample_message.created_at


class TestDirectRequestPayload:
    """DirectRequest の Payload 生成メソッドのテスト。"""

    def test_to_payload_returns_correct_type(self, sample_request):
        """新規作成用 Payload が正しく生成されること。"""
        payload = sample_request.to_payload()
        assert isinstance(payload, RequestPayload)
        assert payload.event_type == FeedEventType.REQUEST
        assert payload.id == sample_request.id

    def test_to_update_payload_returns_correct_type(self, sample_request):
        """更新用 Payload が正しく生成されること。"""
        payload = sample_request.to_update_payload()
        assert isinstance(payload, RequestUpdatePayload)
        assert payload.event_type == FeedEventType.REQUEST_UPDATED
        assert payload.id == sample_request.id
        assert payload.status == sample_request.status


class TestSystemEventPayload:
    """SystemEvent.to_payload のテスト。"""

    def test_join_event(self):
        """JOIN イベントの Payload が正しく生成されること。"""
        event = SystemEvent(type=FeedEventType.JOIN, username=Username("alice"))
        payload = event.to_payload()
        assert payload.event_type == FeedEventType.JOIN
        assert isinstance(payload, SystemEventPayload)
        assert payload.username == Username("alice")

    def test_leave_event(self):
        """LEAVE イベントの Payload が正しく生成されること。"""
        event = SystemEvent(type=FeedEventType.LEAVE, username=Username("bob"))
        payload = event.to_payload()
        assert payload.event_type == FeedEventType.LEAVE
        assert isinstance(payload, SystemEventPayload)
        assert payload.username == Username("bob")
