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
DIRECT_REQUEST_SEQUENCE = SequenceName("direct_request")

# ダイレクトリクエストの per-user inbox シーケンス名の接頭辞。
DIRECT_REQUEST_SEQUENCE_PREFIX = "direct_request:"


def direct_request_sequence(userid: str) -> SequenceName:
    """ユーザーごとの DM 受信ストリーム（inbox）のシーケンス名を返します。

    DM は受信者ごとに独立した連番を持たせるため、``direct_request:{userid}``
    という per-user のシーケンス名で採番・取得する。これにより各クライアントは
    自分の inbox の seq だけを追えばよく、他人の DM による seq の飛びが起きない。

    Args:
        userid: 受信ストリームの所有者ユーザーID。

    Returns:
        ``direct_request:{userid}`` 形式のシーケンス名。
    """
    return SequenceName(f"{DIRECT_REQUEST_SEQUENCE_PREFIX}{userid}")
