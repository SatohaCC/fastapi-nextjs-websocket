"""ドメインエンティティを配信用の Payload に変換するファクトリ。"""

from ..entities.direct_request import DirectRequest
from ..entities.message import Message


class DeliveryFeedFactory:
    """エンティティから配信用フィードのデータ構造（Payload）を生成します。"""

    @staticmethod
    def create_payload_from_message(message: Message) -> tuple[str, dict]:
        """Message エンティティから Payload と event_type を生成します。"""
        payload = {
            "type": "message",
            "username": message.username.value,
            "text": message.text.value,
            # id はオプショナルだが、ここではメインDBのidを含める
            "id": message.id.value if message.id else None,
            "created_at": message.created_at.isoformat(),
        }
        return "message", payload

    @staticmethod
    def create_payload_from_request(request: DirectRequest) -> tuple[str, dict]:
        """DirectRequest エンティティから Payload と event_type を生成します。"""
        payload = {
            "type": "request",
            "id": request.id.value if request.id else None,
            "sender": request.sender.value,
            "recipient": request.recipient.value,
            "text": request.text.value,
            "status": request.status.value,
            "created_at": request.created_at.isoformat(),
            "updated_at": request.updated_at.isoformat(),
        }
        return "request", payload

    @staticmethod
    def create_payload_from_request_updated(request: DirectRequest) -> tuple[str, dict]:
        """更新された DirectRequest エンティティから
        Payload と event_type を生成します。
        """
        payload = {
            "type": "request_updated",
            "id": request.id.value if request.id else None,
            "status": request.status.value,
            "sender": request.sender.value,
            "recipient": request.recipient.value,
            "updated_at": request.updated_at.isoformat(),
        }
        return "request_updated", payload

    @staticmethod
    def create_payload_from_system_event(event_type: str, username: str) -> tuple[str, dict]:
        """入退室などのシステムイベントから Payload を生成します。"""
        payload = {
            "type": event_type,
            "username": username,
        }
        return event_type, payload
