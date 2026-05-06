"""ドメインエンティティを配信用の Payload に変換するファクトリ。"""

from app.domain.primitives.feed import FeedEventType

from ..entities.direct_request import DirectRequest
from ..entities.message import Message
from ..primitives.primitives import Username


class DeliveryFeedFactory:
    """エンティティから配信用フィードのデータ構造（Payload）を生成します。"""

    @staticmethod
    def create_payload_from_message(message: Message) -> tuple[FeedEventType, dict]:
        """Message エンティティから Payload と event_type を生成します。"""
        payload = {
            "type": FeedEventType.MESSAGE.value,
            "username": message.username.value,
            "text": message.text.value,
            # メインDBのidを含める
            "id": message.id.value,
            "created_at": message.created_at.isoformat(),
        }
        return FeedEventType.MESSAGE, payload

    @staticmethod
    def create_payload_from_request(
        request: DirectRequest,
    ) -> tuple[FeedEventType, dict]:
        """DirectRequest エンティティから Payload と event_type を生成します。"""
        payload = {
            "type": FeedEventType.REQUEST.value,
            "id": request.id.value,
            "sender": request.sender.value,
            "recipient": request.recipient.value,
            "text": request.text.value,
            "status": request.status.value,
            "created_at": request.created_at.isoformat(),
            "updated_at": request.updated_at.isoformat(),
        }
        return FeedEventType.REQUEST, payload

    @staticmethod
    def create_payload_from_request_updated(
        request: DirectRequest,
    ) -> tuple[FeedEventType, dict]:
        """更新された DirectRequest エンティティから
        Payload と event_type を生成します。
        """
        payload = {
            "type": FeedEventType.REQUEST_UPDATED.value,
            "id": request.id.value,
            "status": request.status.value,
            "sender": request.sender.value,
            "recipient": request.recipient.value,
            "updated_at": request.updated_at.isoformat(),
        }
        return FeedEventType.REQUEST_UPDATED, payload

    @staticmethod
    def create_payload_from_system_event(
        event_type: FeedEventType, username: Username
    ) -> tuple[FeedEventType, dict]:
        """入退室などのシステムイベントから Payload を生成します。"""
        payload = {
            "type": event_type.value,
            "username": username.value,
        }
        return event_type, payload
