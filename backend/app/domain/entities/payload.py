"""配信フィードに含まれるデータ（Payload）の型定義。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any

from ..primitives.feed import FeedEventType


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

    id: int
    username: str
    text: str
    created_at: str  # ISO format string

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換します。"""
        return {
            "type": self.event_type.value,
            **asdict(self),
        }

    @property
    def event_type(self) -> FeedEventType:
        """イベントタイプを返します。"""
        return FeedEventType.MESSAGE


@dataclass(frozen=True)
class RequestPayload(FeedPayload):
    """ダイレクトリクエスト作成時のペイロード。"""

    id: int
    sender: str
    recipient: str
    text: str
    status: str
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換します。"""
        return {
            "type": self.event_type.value,
            **asdict(self),
        }

    @property
    def event_type(self) -> FeedEventType:
        """イベントタイプを返します。"""
        return FeedEventType.REQUEST


@dataclass(frozen=True)
class RequestUpdatePayload(FeedPayload):
    """ダイレクトリクエスト更新時のペイロード。"""

    id: int
    status: str
    sender: str
    recipient: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換します。"""
        return {
            "type": self.event_type.value,
            **asdict(self),
        }

    @property
    def event_type(self) -> FeedEventType:
        """イベントタイプを返します。"""
        return FeedEventType.REQUEST_UPDATED


@dataclass(frozen=True)
class SystemEventPayload(FeedPayload):
    """入退室などのシステムイベントのペイロード。"""

    type: str  # "join" or "leave"
    username: str

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換します。"""
        return asdict(self)

    @property
    def event_type(self) -> FeedEventType:
        """イベントタイプを返します。"""
        return FeedEventType(self.type)
