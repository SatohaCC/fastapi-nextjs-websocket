"""WebSocket で使用するメッセージスキーマの定義（クライアント↔サーバー）。

命名規則 (CONVENTIONS.md 第 1 節):
    * ``*ClientMessage``: クライアント → サーバー (inbound)
    * ``*ServerMessage``: サーバー → クライアント (outbound)
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal, Optional, Union, cast

from pydantic import BaseModel, ConfigDict, field_validator

from ...domain.primitives.primitives import EntityId, MessageText, TaskText, Username
from ...domain.primitives.task_status import TaskStatus

if TYPE_CHECKING:
    from ...application.outbox.delivery_feed import DeliveryFeed
    from ...application.outbox.payload import (
        DirectRequestPayload,
        DirectRequestUpdatePayload,
        GlobalChatPayload,
        SystemEventPayload,
    )
    from ...domain.entities.message import Message
    from ...domain.entities.task import Task

# --- Client -> Server Messages ---


class PongClientMessage(BaseModel):
    """サーバーからの ping に対する応答メッセージ。"""

    type: Literal["pong"]


class GlobalChatClientMessage(BaseModel):
    """グローバルチャットメッセージ。"""

    type: Literal["global_chat"]
    text: str

    def to_domain(self) -> MessageText:
        """Text フィールドをドメインプリミティブへ変換します。"""
        return MessageText(self.text)


class DirectRequestClientMessage(BaseModel):
    """特定のユーザーへのダイレクトリクエスト送信。"""

    type: Literal["direct_request"]
    to: str
    text: str

    def to_domain(self) -> tuple[Username, TaskText]:
        """To / text フィールドをドメインプリミティブへ変換します。"""
        return Username(self.to), TaskText(self.text)


class UpdateDirectRequestStatusClientMessage(BaseModel):
    """ダイレクトリクエストのステータス更新通知（承諾・拒否など）。"""

    type: Literal["update_status"]
    task_id: int
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """無効なステータス文字列を境界で弾く。"""
        TaskStatus(v)
        return v

    def to_domain(self) -> tuple[EntityId, TaskStatus]:
        """task_id / status をドメインプリミティブへ変換します。"""
        return EntityId(self.task_id), TaskStatus(self.status)


ClientMessage = Union[
    PongClientMessage,
    GlobalChatClientMessage,
    DirectRequestClientMessage,
    UpdateDirectRequestStatusClientMessage,
]


# --- Server -> Client Messages ---


class BaseServerMessage(BaseModel):
    """サーバーからクライアントへ送信するメッセージの基底クラス。

    Note:
        REST API も一部このクラスを ``response_model`` として相乗りで使用している
        (例: GET /api/direct_requests が ``DirectRequestServerMessage`` を返す)。
        構造的には REST 専用 ``*Response`` の切り出しが望ましいが、
        現段階では wire 互換性維持のため共有している。
    """

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_domain(cls, entity: Any, is_history: bool = False) -> "BaseServerMessage":
        """ドメインエンティティからレスポンスモデルを生成します。"""
        raise NotImplementedError


class GlobalChatServerMessage(BaseServerMessage):
    """グローバルチャットメッセージのレスポンス。"""

    type: Literal["global_chat"] = "global_chat"
    id: int
    seq: Optional[int] = None
    username: str
    text: str
    created_at: datetime
    is_history: bool = False

    @classmethod
    def from_domain(
        cls, entity: Union["Message", "GlobalChatPayload"], is_history: bool = False
    ) -> "GlobalChatServerMessage":
        """ドメインエンティティまたはペイロードからレスポンスモデルを生成します。"""
        return cls(
            id=entity.id.value,
            username=entity.username.value,
            text=entity.text.value,
            created_at=entity.created_at,
            is_history=is_history,
        )


class DirectRequestServerMessage(BaseServerMessage):
    """ダイレクトリクエストの詳細レスポンス。"""

    type: Literal["direct_request"] = "direct_request"
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
        entity: Union["Task", "DirectRequestPayload"],
        is_history: bool = False,
    ) -> "DirectRequestServerMessage":
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


class DirectRequestUpdatedServerMessage(BaseServerMessage):
    """ダイレクトリクエストのステータスが更新された際の通知レスポンス。"""

    type: Literal["direct_request_updated"] = "direct_request_updated"
    id: int
    seq: Optional[int] = None
    status: str
    sender: str
    recipient: str
    updated_at: datetime

    @classmethod
    def from_domain(
        cls, entity: "DirectRequestUpdatePayload", is_history: bool = False
    ) -> "DirectRequestUpdatedServerMessage":
        """DirectRequestUpdatePayload からレスポンスモデルを生成します。"""
        return cls(
            id=entity.id.value,
            status=entity.status.value,
            sender=entity.sender.value,
            recipient=entity.recipient.value,
            updated_at=entity.updated_at,
        )


class JoinLeaveServerMessage(BaseServerMessage):
    """ユーザーの入退室通知。"""

    type: Literal["join", "leave"]
    username: str

    @classmethod
    def from_domain(
        cls, entity: "SystemEventPayload", is_history: bool = False
    ) -> "JoinLeaveServerMessage":
        """SystemEventPayload からレスポンスモデルを生成します。"""
        return cls(
            type=cast(Literal["join", "leave"], entity.type.value),
            username=entity.username.value,
        )


class ErrorServerMessage(BaseModel):
    """エラー発生時のレスポンス。"""

    type: Literal["error"] = "error"
    text: str


def create_server_message_from_feed(
    feed: "DeliveryFeed", is_history: bool = False
) -> BaseServerMessage:
    """DeliveryFeed から適切な ServerMessage DTO を生成します。"""
    from ...application.outbox.payload import (
        DirectRequestPayload,
        DirectRequestUpdatePayload,
        GlobalChatPayload,
        SystemEventPayload,
    )

    payload = feed.payload
    resp: BaseServerMessage

    if isinstance(payload, GlobalChatPayload):
        resp = GlobalChatServerMessage.from_domain(payload, is_history=is_history)
    elif isinstance(payload, DirectRequestPayload):
        resp = DirectRequestServerMessage.from_domain(payload, is_history=is_history)
    elif isinstance(payload, DirectRequestUpdatePayload):
        resp = DirectRequestUpdatedServerMessage.from_domain(
            payload, is_history=is_history
        )
    elif isinstance(payload, SystemEventPayload):
        resp = JoinLeaveServerMessage.from_domain(payload, is_history=is_history)
    else:
        raise ValueError(f"Unsupported payload type: {type(payload)}")

    # sequence_id がある場合は seq フィールドを設定
    if hasattr(resp, "seq"):
        resp.seq = feed.sequence_id.value  # type: ignore[attr-defined]

    return resp
