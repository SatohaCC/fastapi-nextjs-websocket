"""WebSocket で使用するメッセージスキーマの定義（クライアント↔サーバー）。"""

from datetime import datetime
from typing import Literal, Optional, Union

from pydantic import BaseModel

from ...domain.entities.direct_request import DirectRequest
from ...domain.entities.message import Message
from ...domain.primitives.feed import SequenceId
from ...domain.primitives.primitives import EntityId, MessageText, RequestText, Username
from ...domain.primitives.request_status import RequestStatus


# --- Client -> Server Messages (Requests) ---


class PongMessage(BaseModel):
    """サーバーからの ping に対する応答メッセージ。"""

    type: Literal["pong"]


class ChatMessage(BaseModel):
    """一般チャットメッセージ。"""

    type: Literal["message"]
    text: str

    def to_domain(self) -> MessageText:
        """text フィールドをドメインプリミティブへ変換します。"""
        return MessageText(self.text)


class RequestMessage(BaseModel):
    """特定のユーザーへのダイレクトリクエスト送信。"""

    type: Literal["request"]
    to: str
    text: str

    def to_domain(self) -> tuple[Username, RequestText]:
        """to / text フィールドをドメインプリミティブへ変換します。"""
        return Username(self.to), RequestText(self.text)


class StatusUpdateMessage(BaseModel):
    """リクエストのステータス更新通知（承諾・拒否など）。"""

    type: Literal["update_status"]
    request_id: int
    status: RequestStatus

    def to_domain(self) -> tuple[EntityId, RequestStatus]:
        """request_id フィールドをドメインプリミティブへ変換します。"""
        return EntityId(self.request_id), self.status


WebSocketMessage = Union[PongMessage, ChatMessage, RequestMessage, StatusUpdateMessage]


# --- Server -> Client Messages (Responses) ---


class ChatResponse(BaseModel):
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
        cls,
        msg: Message,
        is_history: bool = False,
        seq: Optional[SequenceId] = None,
    ) -> "ChatResponse":
        """Message エンティティからレスポンス DTO を生成します。"""
        return cls(
            id=msg.id.value,
            seq=seq.value if seq is not None else None,
            username=msg.username.value,
            text=msg.text.value,
            created_at=msg.created_at,
            is_history=is_history,
        )


class RequestResponse(BaseModel):
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
        cls,
        req: DirectRequest,
        is_history: bool = False,
        seq: Optional[SequenceId] = None,
    ) -> "RequestResponse":
        """DirectRequest エンティティからレスポンス DTO を生成します。"""
        return cls(
            id=req.id.value,
            seq=seq.value if seq is not None else None,
            sender=req.sender.value,
            recipient=req.recipient.value,
            text=req.text.value,
            status=req.status,
            created_at=req.created_at,
            updated_at=req.updated_at,
            is_history=is_history,
        )


class RequestUpdateResponse(BaseModel):
    """リクエストステータスが更新された際の通知レスポンス。"""

    type: Literal["request_updated"] = "request_updated"
    id: int
    seq: Optional[int] = None
    status: RequestStatus
    sender: str
    recipient: str
    updated_at: datetime

    @classmethod
    def from_domain(
        cls,
        req: DirectRequest,
        seq: Optional[SequenceId] = None,
    ) -> "RequestUpdateResponse":
        """DirectRequest エンティティからレスポンス DTO を生成します。"""
        return cls(
            id=req.id.value,
            seq=seq.value if seq is not None else None,
            status=req.status,
            sender=req.sender.value,
            recipient=req.recipient.value,
            updated_at=req.updated_at,
        )


class JoinLeaveResponse(BaseModel):
    """ユーザーの入退室通知。"""

    type: Literal["join", "leave"]
    username: str

    @classmethod
    def from_domain(
        cls, type: Literal["join", "leave"], username: Username
    ) -> "JoinLeaveResponse":
        """Username ドメインプリミティブからレスポンス DTO を生成します。"""
        return cls(type=type, username=username.value)


class ErrorResponse(BaseModel):
    """エラー発生時のレスポンス。"""

    type: Literal["error"] = "error"
    text: str
