"""WebSocket で使用するメッセージスキーマの定義（クライアント↔サーバー）。"""

from datetime import datetime
from typing import Literal, Optional, Union

from pydantic import BaseModel, ConfigDict

from ...domain.entities.direct_request import RequestStatus

# --- Client -> Server Messages (Requests) ---


class PongMessage(BaseModel):
    """サーバーからの ping に対する応答メッセージ。"""

    type: Literal["pong"]


class ChatMessage(BaseModel):
    """一般チャットメッセージ。"""

    type: Literal["message"]
    text: str


class RequestMessage(BaseModel):
    """特定のユーザーへのダイレクトリクエスト送信。"""

    type: Literal["request"]
    to: str
    text: str


class StatusUpdateMessage(BaseModel):
    """リクエストのステータス更新通知（承諾・拒否など）。"""

    type: Literal["update_status"]
    request_id: int
    status: RequestStatus


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


class RequestUpdateResponse(BaseResponse):
    """リクエストステータスが更新された際の通知レスポンス。"""

    type: Literal["request_updated"] = "request_updated"
    id: int
    seq: Optional[int] = None
    status: RequestStatus
    sender: str
    recipient: str
    updated_at: datetime


class JoinLeaveResponse(BaseModel):
    """ユーザーの入退室通知。"""

    type: Literal["join", "leave"]
    username: str


class ErrorResponse(BaseModel):
    """エラー発生時のレスポンス。"""

    type: Literal["error"] = "error"
    text: str
