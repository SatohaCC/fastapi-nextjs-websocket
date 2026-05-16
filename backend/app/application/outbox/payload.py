"""配信フィードに含まれるデータ（Payload）の型定義。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from ...domain.primitives.feed import FeedEventType
from ...domain.primitives.primitives import EntityId, MessageText, RequestText, Username
from ...domain.primitives.request_status import RequestStatus


@dataclass(frozen=True)
class FeedPayload(ABC):
    """配信フィードのペイロードの基底クラス。"""

    @property
    @abstractmethod
    def event_type(self) -> FeedEventType:
        """このペイロードに対応するイベントタイプ。"""
        pass


@dataclass(frozen=True)
class GlobalChatPayload(FeedPayload):
    """グローバルチャットメッセージのペイロード。"""

    id: EntityId
    username: Username
    text: MessageText
    created_at: datetime

    @property
    def event_type(self) -> FeedEventType:
        """イベントタイプを返します。"""
        return FeedEventType.GLOBAL_CHAT


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

    @property
    def event_type(self) -> FeedEventType:
        """イベントタイプを返します。"""
        return FeedEventType.REQUEST_UPDATED


@dataclass(frozen=True)
class SystemEventPayload(FeedPayload):
    """入退室などのシステムイベントのペイロード。"""

    type: FeedEventType
    username: Username

    @property
    def event_type(self) -> FeedEventType:
        """イベントタイプを返します。"""
        return self.type
