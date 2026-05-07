"""DeliveryFeedFactory の Payload 生成ロジックのユニットテスト。"""

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
from app.domain.factories.delivery_feed_factory import DeliveryFeedFactory
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


class TestCreatePayloadFromMessage:
    """DeliveryFeedFactory.create_payload_from_message のテスト。"""

    def test_returns_message_event_type(self, sample_message):
        """event_type が FeedEventType.MESSAGE であること。"""
        event_type, _ = DeliveryFeedFactory.create_payload_from_message(sample_message)
        assert event_type == FeedEventType.MESSAGE

    def test_returns_message_payload_instance(self, sample_message):
        """Payload が MessagePayload のインスタンスであること。"""
        _, payload = DeliveryFeedFactory.create_payload_from_message(sample_message)
        assert isinstance(payload, MessagePayload)

    def test_payload_fields_match_message(self, sample_message):
        """Payload のフィールドが元のメッセージと一致すること。"""
        _, payload = DeliveryFeedFactory.create_payload_from_message(sample_message)
        assert payload.id == sample_message.id
        assert payload.username == sample_message.username
        assert payload.text == sample_message.text
        assert payload.created_at == sample_message.created_at


class TestCreatePayloadFromRequest:
    """DeliveryFeedFactory.create_payload_from_request のテスト。"""

    def test_returns_request_event_type(self, sample_request):
        """event_type が FeedEventType.REQUEST であること。"""
        event_type, _ = DeliveryFeedFactory.create_payload_from_request(sample_request)
        assert event_type == FeedEventType.REQUEST

    def test_returns_request_payload_instance(self, sample_request):
        """Payload が RequestPayload のインスタンスであること。"""
        _, payload = DeliveryFeedFactory.create_payload_from_request(sample_request)
        assert isinstance(payload, RequestPayload)

    def test_payload_fields_match_request(self, sample_request):
        """Payload のフィールドが元のリクエストと一致すること。"""
        _, payload = DeliveryFeedFactory.create_payload_from_request(sample_request)
        assert payload.id == sample_request.id
        assert payload.sender == sample_request.sender
        assert payload.recipient == sample_request.recipient
        assert payload.status == sample_request.status


class TestCreatePayloadFromRequestUpdated:
    """DeliveryFeedFactory.create_payload_from_request_updated のテスト。"""

    def test_returns_request_updated_event_type(self, sample_request):
        """event_type が FeedEventType.REQUEST_UPDATED であること。"""
        event_type, _ = DeliveryFeedFactory.create_payload_from_request_updated(
            sample_request
        )
        assert event_type == FeedEventType.REQUEST_UPDATED

    def test_returns_request_update_payload_instance(self, sample_request):
        """Payload が RequestUpdatePayload のインスタンスであること。"""
        _, payload = DeliveryFeedFactory.create_payload_from_request_updated(
            sample_request
        )
        assert isinstance(payload, RequestUpdatePayload)

    def test_payload_fields_match_request(self, sample_request):
        """Payload のフィールドが元のリクエストと一致すること。"""
        _, payload = DeliveryFeedFactory.create_payload_from_request_updated(
            sample_request
        )
        assert payload.id == sample_request.id
        assert payload.status == sample_request.status
        assert payload.sender == sample_request.sender
        assert payload.recipient == sample_request.recipient


class TestCreatePayloadFromSystemEvent:
    """DeliveryFeedFactory.create_payload_from_system_event のテスト。"""

    def test_join_event(self):
        """JOIN イベントで正しい event_type と payload が返ること。"""
        event_type, payload = DeliveryFeedFactory.create_payload_from_system_event(
            FeedEventType.JOIN, Username("alice")
        )
        assert event_type == FeedEventType.JOIN
        assert isinstance(payload, SystemEventPayload)
        assert payload.username == Username("alice")

    def test_leave_event(self):
        """LEAVE イベントで正しい event_type と payload が返ること。"""
        event_type, payload = DeliveryFeedFactory.create_payload_from_system_event(
            FeedEventType.LEAVE, Username("bob")
        )
        assert event_type == FeedEventType.LEAVE
        assert isinstance(payload, SystemEventPayload)
