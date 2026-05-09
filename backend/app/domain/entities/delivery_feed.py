"""配信フィードを表すドメインエンティティ。"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone

from app.domain.primitives.feed import (
    FeedEventType,
    FeedStatus,
    SequenceId,
    SequenceName,
)

from .payload import FeedPayload


@dataclass(frozen=True, kw_only=True)
class DraftDeliveryFeed:
    """Outbox 新規登録用のドメインエンティティ（Command 側）。

    アプリケーション層でフィードを生成する際に使用します。
    永続化前のため sequence_id を持ちません。
    """

    sequence_name: SequenceName
    event_type: FeedEventType
    payload: FeedPayload
    status: FeedStatus = FeedStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, kw_only=True)
class DeliveryFeed(DraftDeliveryFeed):
    """永続化済み配信フィードのドメインエンティティ（Query 側 + ステータス遷移）。

    DB保存後にリポジトリから返されるエンティティです。
    sequence_id は必ず存在し、None チェックは不要です。
    """

    sequence_id: SequenceId

    def mark_processed(self) -> DeliveryFeed:
        """配信済みステータスの新しいインスタンスを返します。"""
        return replace(self, status=FeedStatus.PROCESSED)

    def mark_failed(self) -> DeliveryFeed:
        """配信失敗ステータスの新しいインスタンスを返します。"""
        return replace(self, status=FeedStatus.FAILED)
