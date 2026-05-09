"""WebSocket で使用するメッセージスキーマの定義（クライアント↔サーバー）。"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal, Optional, Union, cast

from pydantic import BaseModel, ConfigDict, field_validator

from ...domain.entities.direct_request import RequestStatus
from ...domain.primitives.primitives import EntityId, MessageText, RequestText, Username

if TYPE_CHECKING:
    from ...application.outbox.delivery_feed import DeliveryFeed
    from ...application.outbox.payload import (
        MessagePayload,
        RequestPayload,
        RequestUpdatePayload,
        SystemEventPayload,
    )
    from ...domain.entities.direct_request import DirectRequest
    from ...domain.entities.message import Message

# --- Client -> Server Messages (Requests) ---


class PongMessage(BaseModel):
    """サーバーからの ping に対する応答メッセージ。"""

    type: Literal["pong"]


class ChatMessage(BaseModel):
    """一般チャットメッセージ。"""

    type: Literal["message"]
    text: str

    def to_domain(self) -> MessageText:
        """Text フィールドをドメインプリミティブへ変換します。"""
        return MessageText(self.text)


class RequestMessage(BaseModel):
    """特定のユーザーへのダイレクトリクエスト送信。"""

    type: Literal["request"]
    to: str
    text: str

    def to_domain(self) -> tuple[Username, RequestText]:
        """To / text フィールドをドメインプリミティブへ変換します。"""
        return Username(self.to), RequestText(self.text)


class StatusUpdateMessage(BaseModel):
    """リクエストのステータス更新通知（承諾・拒否など）。"""

    type: Literal["update_status"]
    request_id: int
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """無効なステータス文字列を境界で弾く。"""
        RequestStatus(v)
        return v

    def to_domain(self) -> tuple[EntityId, RequestStatus]:
        """request_id / status をドメインプリミティブへ変換します。"""
        return EntityId(self.request_id), RequestStatus(self.status)


WebSocketMessage = Union[PongMessage, ChatMessage, RequestMessage, StatusUpdateMessage]


# --- Server -> Client Messages (Responses) ---


class BaseResponse(BaseModel):
    """サーバーからクライアントへ送信するレスポンスの基底クラス。"""

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_domain(cls, entity: Any, is_history: bool = False) -> "BaseResponse":
        """ドメインエンティティからレスポンスモデルを生成します。"""
        raise NotImplementedError


class ChatResponse(BaseResponse):
    """チャットメッセージのレスポンス。"""

    type: Literal["message"] = "message"
    id: int
    seq: Optional[int] = None
    username: str
    text: str
    created_at: datetime
    is_history: bool = False

    @classmethod
    def from_domain(
        cls, entity: Union["Message", "MessagePayload"], is_history: bool = False
    ) -> "ChatResponse":
        """ドメインエンティティまたはペイロードからレスポンスモデルを生成します。"""
        return cls(
            id=entity.id.value,
            username=entity.username.value,
            text=entity.text.value,
            created_at=entity.created_at,
            is_history=is_history,
        )


class RequestResponse(BaseResponse):
    """ダイレクトリクエストの詳細レスポンス。"""

    type: Literal["request"] = "request"
    id: int
    seq: Optional[int] = None
    sender: str
    recipient: str
    text: str
    status: str
    created_at: datetime
    updated_at: datetime
    is_history: bool = False

    @classmethod
    def from_domain(
        cls,
        entity: Union["DirectRequest", "RequestPayload"],
        is_history: bool = False,
    ) -> "RequestResponse":
        """ドメインエンティティまたはペイロードからレスポンスモデルを生成します。"""
        return cls(
            id=entity.id.value,
            sender=entity.sender.value,
            recipient=entity.recipient.value,
            text=entity.text.value,
            status=entity.status.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_history=is_history,
        )


class RequestUpdateResponse(BaseResponse):
    """リクエストステータスが更新された際の通知レスポンス。"""

    type: Literal["request_updated"] = "request_updated"
    id: int
    seq: Optional[int] = None
    status: str
    sender: str
    recipient: str
    updated_at: datetime

    @classmethod
    def from_domain(
        cls, entity: "RequestUpdatePayload", is_history: bool = False
    ) -> "RequestUpdateResponse":
        """RequestUpdatePayload からレスポンスモデルを生成します。"""
        return cls(
            id=entity.id.value,
            status=entity.status.value,
            sender=entity.sender.value,
            recipient=entity.recipient.value,
            updated_at=entity.updated_at,
        )


class JoinLeaveResponse(BaseResponse):
    """ユーザーの入退室通知。"""

    type: Literal["join", "leave"]
    username: str

    @classmethod
    def from_domain(
        cls, entity: "SystemEventPayload", is_history: bool = False
    ) -> "JoinLeaveResponse":
        """SystemEventPayload からレスポンスモデルを生成します。"""
        return cls(
            type=cast(Literal["join", "leave"], entity.type.value),
            username=entity.username.value,
        )


class ErrorResponse(BaseModel):
    """エラー発生時のレスポンス。"""

    type: Literal["error"] = "error"
    text: str


def create_response_from_feed(
    feed: "DeliveryFeed", is_history: bool = False
) -> BaseResponse:
    """DeliveryFeed から適切なレスポンス DTO を生成します。"""
    from ...application.outbox.payload import (
        MessagePayload,
        RequestPayload,
        RequestUpdatePayload,
        SystemEventPayload,
    )

    payload = feed.payload
    resp: BaseResponse

    if isinstance(payload, MessagePayload):
        resp = ChatResponse.from_domain(payload, is_history=is_history)
    elif isinstance(payload, RequestPayload):
        resp = RequestResponse.from_domain(payload, is_history=is_history)
    elif isinstance(payload, RequestUpdatePayload):
        resp = RequestUpdateResponse.from_domain(payload, is_history=is_history)
    elif isinstance(payload, SystemEventPayload):
        resp = JoinLeaveResponse.from_domain(payload, is_history=is_history)
    else:
        raise ValueError(f"Unsupported payload type: {type(payload)}")

    # sequence_id がある場合は seq フィールドを設定
    if hasattr(resp, "seq"):
        resp.seq = feed.sequence_id.value  # type: ignore[attr-defined]

    return resp
