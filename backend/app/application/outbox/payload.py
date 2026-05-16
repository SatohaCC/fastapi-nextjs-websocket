"""配信フィードに含まれるデータ（Payload）の型定義。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from ...domain.primitives.feed import FeedEventType
from ...domain.primitives.primitives import EntityId, MessageText, TaskText, Username
from ...domain.primitives.task_status import TaskStatus


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
class DirectRequestPayload(FeedPayload):
    """ダイレクトリクエスト作成時のペイロード。"""

    id: EntityId
    sender: Username
    recipient: Username
    text: TaskText
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    @property
    def event_type(self) -> FeedEventType:
        """イベントタイプを返します。"""
        return FeedEventType.DIRECT_REQUEST


@dataclass(frozen=True)
class DirectRequestUpdatePayload(FeedPayload):
    """ダイレクトリクエスト更新時のペイロード。"""

    id: EntityId
    status: TaskStatus
    sender: Username
    recipient: Username
    updated_at: datetime

    @property
    def event_type(self) -> FeedEventType:
        """イベントタイプを返します。"""
        return FeedEventType.DIRECT_REQUEST_UPDATED


@dataclass(frozen=True)
class SystemEventPayload(FeedPayload):
    """入退室などのシステムイベントのペイロード。"""

    type: FeedEventType
    username: Username

    @property
    def event_type(self) -> FeedEventType:
        """イベントタイプを返します。"""
        return self.type
