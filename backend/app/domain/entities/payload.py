"""配信フィードに含まれるデータ（Payload）の型定義。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ..primitives.feed import FeedEventType
from ..primitives.primitives import EntityId, MessageText, RequestText, Username
from ..primitives.request_status import RequestStatus


@dataclass(frozen=True)
class FeedPayload(ABC):
    """配信フィードのペイロードの基底クラス。"""

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換します。JSON シリアライズに使用します。"""
        pass

    @property
    @abstractmethod
    def event_type(self) -> FeedEventType:
        """このペイロードに対応するイベントタイプ。"""
        pass


@dataclass(frozen=True)
class MessagePayload(FeedPayload):
    """チャットメッセージのペイロード。"""

    id: EntityId
    username: Username
    text: MessageText
    created_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換します。"""
        return {
            "type": self.event_type.value,
            "id": self.id.value,
            "username": self.username.value,
            "text": self.text.value,
            "created_at": self.created_at.isoformat(),
        }

    @property
    def event_type(self) -> FeedEventType:
        """イベントタイプを返します。"""
        return FeedEventType.MESSAGE


@dataclass(frozen=True)
class RequestPayload(FeedPayload):
    """ダイレクトリクエスト作成時のペイロード。"""

    id: EntityId
    sender: Username
    recipient: Username
    text: RequestText
    status: RequestStatus
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換します。"""
        return {
            "type": self.event_type.value,
            "id": self.id.value,
            "sender": self.sender.value,
            "recipient": self.recipient.value,
            "text": self.text.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @property
    def event_type(self) -> FeedEventType:
        """イベントタイプを返します。"""
        return FeedEventType.REQUEST


@dataclass(frozen=True)
class RequestUpdatePayload(FeedPayload):
    """ダイレクトリクエスト更新時のペイロード。"""

    id: EntityId
    status: RequestStatus
    sender: Username
    recipient: Username
    updated_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換します。"""
        return {
            "type": self.event_type.value,
            "id": self.id.value,
            "status": self.status.value,
            "sender": self.sender.value,
            "recipient": self.recipient.value,
            "updated_at": self.updated_at.isoformat(),
        }

    @property
    def event_type(self) -> FeedEventType:
        """イベントタイプを返します。"""
        return FeedEventType.REQUEST_UPDATED


@dataclass(frozen=True)
class SystemEventPayload(FeedPayload):
    """入退室などのシステムイベントのペイロード。"""

    type: FeedEventType
    username: Username

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換します。"""
        return {
            "type": self.type.value,
            "username": self.username.value,
        }

    @property
    def event_type(self) -> FeedEventType:
        """イベントタイプを返します。"""
        return self.type
