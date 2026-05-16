"""ドメインオブジェクトとシリアライズ形式（辞書）の相互変換を行うユーティリティ。"""

from datetime import datetime
from typing import Any

from ..application.outbox.delivery_feed import (
    DeliveryFeed,
    FeedStatus,
    SequenceId,
    SequenceName,
)
from ..application.outbox.payload import (
    FeedPayload,
    GlobalChatPayload,
    RequestPayload,
    RequestUpdatePayload,
    SystemEventPayload,
)
from ..domain.primitives.feed import FeedEventType
from ..domain.primitives.primitives import (
    EntityId,
    MessageText,
    RequestText,
    Username,
)
from ..domain.primitives.request_status import RequestStatus


def payload_to_dict(payload: FeedPayload) -> dict[str, Any]:
    """FeedPayload を JSON シリアライズ可能な辞書に変換します。"""
    if isinstance(payload, GlobalChatPayload):
        return {
            "id": payload.id.value,
            "username": payload.username.value,
            "text": payload.text.value,
            "created_at": payload.created_at.isoformat(),
        }
    elif isinstance(payload, RequestPayload):
        return {
            "id": payload.id.value,
            "sender": payload.sender.value,
            "recipient": payload.recipient.value,
            "text": payload.text.value,
            "status": payload.status.value,
            "created_at": payload.created_at.isoformat(),
            "updated_at": payload.updated_at.isoformat(),
        }
    elif isinstance(payload, RequestUpdatePayload):
        return {
            "id": payload.id.value,
            "status": payload.status.value,
            "sender": payload.sender.value,
            "recipient": payload.recipient.value,
            "updated_at": payload.updated_at.isoformat(),
        }
    elif isinstance(payload, SystemEventPayload):
        return {
            "type": payload.type.value,
            "username": payload.username.value,
        }
    raise ValueError(f"Unknown payload type: {type(payload)}")


def dict_to_payload(event_type: FeedEventType, data: dict[str, Any]) -> FeedPayload:
    """辞書から FeedPayload を再構成します。"""
    if event_type == FeedEventType.GLOBAL_CHAT:
        return GlobalChatPayload(
            id=EntityId(data["id"]),
            username=Username(data["username"]),
            text=MessageText(data["text"]),
            created_at=datetime.fromisoformat(data["created_at"]),
        )
    elif event_type == FeedEventType.REQUEST:
        return RequestPayload(
            id=EntityId(data["id"]),
            sender=Username(data["sender"]),
            recipient=Username(data["recipient"]),
            text=RequestText(data["text"]),
            status=RequestStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
    elif event_type == FeedEventType.REQUEST_UPDATED:
        return RequestUpdatePayload(
            id=EntityId(data["id"]),
            status=RequestStatus(data["status"]),
            sender=Username(data["sender"]),
            recipient=Username(data["recipient"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
    else:
        return SystemEventPayload(
            type=FeedEventType(data["type"]),
            username=Username(data["username"]),
        )


def feed_to_dict(feed: DeliveryFeed) -> dict[str, Any]:
    """DeliveryFeed を中継用（Redis等）の辞書に変換します。"""
    return {
        "sequence_name": feed.sequence_name.value,
        "sequence_id": feed.sequence_id.value,
        "event_type": feed.event_type.value,
        "payload": payload_to_dict(feed.payload),
        "status": feed.status.value,
        "created_at": feed.created_at.isoformat(),
    }


def dict_to_feed(data: dict[str, Any]) -> DeliveryFeed:
    """辞書から DeliveryFeed を再構成します。"""
    event_type = FeedEventType(data["event_type"])
    return DeliveryFeed(
        sequence_name=SequenceName(data["sequence_name"]),
        sequence_id=SequenceId(data["sequence_id"]),
        event_type=event_type,
        payload=dict_to_payload(event_type, data["payload"]),
        status=FeedStatus(data["status"]),
        created_at=datetime.fromisoformat(data["created_at"]),
    )
