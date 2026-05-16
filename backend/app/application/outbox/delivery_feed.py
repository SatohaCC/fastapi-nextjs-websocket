"""Outbox パターンで使用する配信フィードと関連プリミティブの定義。"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum

from ...domain.primitives.feed import FeedEventType
from ..outbox.payload import FeedPayload


@dataclass(frozen=True)
class SequenceName:
    """配信シーケンス名を表すアプリケーションプリミティブ。"""

    value: str

    def __post_init__(self) -> None:
        """シーケンス名のバリデーション。"""
        if not self.value or not self.value.strip():
            raise ValueError("Sequence name cannot be empty")

    def __str__(self) -> str:
        """文字列としての表現を返します。"""
        return self.value


@dataclass(frozen=True)
class SequenceId:
    """配信シーケンス ID を表すアプリケーションプリミティブ。"""

    value: int

    def __post_init__(self) -> None:
        """シーケンス ID のバリデーション。"""
        if self.value < 0:
            raise ValueError("Sequence ID must be non-negative")

    def __str__(self) -> str:
        """文字列としての表現を返します。"""
        return str(self.value)


class FeedStatus(str, Enum):
    """Outbox レコードの配信状態を表す列挙型。"""

    __slots__ = ()
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


@dataclass(frozen=True, kw_only=True)
class DraftDeliveryFeed:
    """Outbox 新規登録用のオブジェクト（永続化前）。"""

    sequence_name: SequenceName
    event_type: FeedEventType
    payload: FeedPayload
    status: FeedStatus = FeedStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, kw_only=True)
class DeliveryFeed(DraftDeliveryFeed):
    """永続化済み配信フィード。"""

    sequence_id: SequenceId

    def mark_processed(self) -> DeliveryFeed:
        """配信済みステータスの新しいインスタンスを返します。"""
        return replace(self, status=FeedStatus.PROCESSED)

    def mark_failed(self) -> DeliveryFeed:
        """配信失敗ステータスの新しいインスタンスを返します。"""
        return replace(self, status=FeedStatus.FAILED)


# シーケンス名定数（魔法文字列の一元管理）
GLOBAL_CHAT_SEQUENCE = SequenceName("global_chat")
SYSTEM_SEQUENCE = SequenceName("system_global")
REQUESTS_SEQUENCE = SequenceName("requests_global")
