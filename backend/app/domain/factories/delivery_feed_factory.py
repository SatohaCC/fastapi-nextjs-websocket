"""ドメインエンティティを配信用の Payload に変換するファクトリ。"""

from app.domain.primitives.feed import FeedEventType

from ..entities.direct_request import DirectRequest
from ..entities.message import Message
from ..entities.payload import (
    FeedPayload,
    MessagePayload,
    RequestPayload,
    RequestUpdatePayload,
    SystemEventPayload,
)
from ..primitives.primitives import Username


class DeliveryFeedFactory:
    """エンティティから配信用フィードのデータ構造（Payload）を生成します。"""

    @staticmethod
    def create_payload_from_message(
        message: Message,
    ) -> tuple[FeedEventType, FeedPayload]:
        """Message エンティティから Payload と event_type を生成します。"""
        payload = MessagePayload(
            id=message.id,
            username=message.username,
            text=message.text,
            created_at=message.created_at,
        )
        return FeedEventType.MESSAGE, payload

    @staticmethod
    def create_payload_from_request(
        request: DirectRequest,
    ) -> tuple[FeedEventType, FeedPayload]:
        """DirectRequest エンティティから Payload と event_type を生成します。"""
        payload = RequestPayload(
            id=request.id,
            sender=request.sender,
            recipient=request.recipient,
            text=request.text,
            status=request.status,
            created_at=request.created_at,
            updated_at=request.updated_at,
        )
        return FeedEventType.REQUEST, payload

    @staticmethod
    def create_payload_from_request_updated(
        request: DirectRequest,
    ) -> tuple[FeedEventType, FeedPayload]:
        """更新された DirectRequest エンティティから
        Payload と event_type を生成します。
        """
        payload = RequestUpdatePayload(
            id=request.id,
            status=request.status,
            sender=request.sender,
            recipient=request.recipient,
            updated_at=request.updated_at,
        )
        return FeedEventType.REQUEST_UPDATED, payload

    @staticmethod
    def create_payload_from_system_event(
        event_type: FeedEventType, username: Username
    ) -> tuple[FeedEventType, FeedPayload]:
        """入退室などのシステムイベントから Payload を生成します。"""
        payload = SystemEventPayload(
            type=event_type,
            username=username,
        )
        return event_type, payload
