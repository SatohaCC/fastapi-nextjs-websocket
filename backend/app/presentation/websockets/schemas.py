"""WebSocket で使用するメッセージスキーマの定義（クライアント↔サーバー）。"""

from datetime import datetime
from typing import TYPE_CHECKING, Literal, Optional, Union, cast

from pydantic import BaseModel, ConfigDict

from ...domain.entities.direct_request import RequestStatus
from ...domain.primitives.primitives import EntityId, MessageText, RequestText, Username

if TYPE_CHECKING:
    from ...domain.entities.direct_request import DirectRequest
    from ...domain.entities.message import Message
    from ...domain.entities.payload import RequestUpdatePayload, SystemEventPayload

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
    status: RequestStatus

    def to_domain(self) -> tuple[EntityId, RequestStatus]:
        """request_id / status をドメインプリミティブへ変換します。"""
        return EntityId(self.request_id), self.status


WebSocketMessage = Union[PongMessage, ChatMessage, RequestMessage, StatusUpdateMessage]


# --- Server -> Client Messages (Responses) ---


class BaseResponse(BaseModel):
    """サーバーからクライアントへ送信するレスポンスの基底クラス。"""

    model_config = ConfigDict(from_attributes=True)


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
        cls, message: "Message", is_history: bool = False
    ) -> "ChatResponse":
        """ドメインエンティティからレスポンスモデルを生成します。"""
        return cls(
            id=message.id.value,
            username=message.username.value,
            text=message.text.value,
            created_at=message.created_at,
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
    status: RequestStatus
    created_at: datetime
    updated_at: datetime
    is_history: bool = False

    @classmethod
    def from_domain(
        cls, request: "DirectRequest", is_history: bool = False
    ) -> "RequestResponse":
        """ドメインエンティティからレスポンスモデルを生成します。"""
        return cls(
            id=request.id.value,
            sender=request.sender.value,
            recipient=request.recipient.value,
            text=request.text.value,
            status=request.status,
            created_at=request.created_at,
            updated_at=request.updated_at,
            is_history=is_history,
        )


class RequestUpdateResponse(BaseResponse):
    """リクエストステータスが更新された際の通知レスポンス。"""

    type: Literal["request_updated"] = "request_updated"
    id: int
    seq: Optional[int] = None
    status: RequestStatus
    sender: str
    recipient: str
    updated_at: datetime

    @classmethod
    def from_domain(cls, payload: "RequestUpdatePayload") -> "RequestUpdateResponse":
        """RequestUpdatePayload からレスポンスモデルを生成します。"""
        return cls(
            id=payload.id.value,
            status=payload.status,
            sender=payload.sender.value,
            recipient=payload.recipient.value,
            updated_at=payload.updated_at,
        )


class JoinLeaveResponse(BaseModel):
    """ユーザーの入退室通知。"""

    type: Literal["join", "leave"]
    username: str

    @classmethod
    def from_domain(cls, payload: "SystemEventPayload") -> "JoinLeaveResponse":
        """SystemEventPayload からレスポンスモデルを生成します。"""
        return cls(
            type=cast(Literal["join", "leave"], payload.type.value),
            username=payload.username.value,
        )


class ErrorResponse(BaseModel):
    """エラー発生時のレスポンス。"""

    type: Literal["error"] = "error"
    text: str
