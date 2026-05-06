"""配信フィードを表すドメインエンティティ。"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any

from app.domain.primitives.feed import (
    FeedEventType,
    FeedStatus,
    SequenceId,
    SequenceName,
)


@dataclass(frozen=True, kw_only=True)
class DeliveryFeed:
    """Outbox に記録される配信フィードデータ。"""

    sequence_name: SequenceName
    sequence_id: SequenceId | None = None
    event_type: FeedEventType
    payload: dict[str, Any]
    status: FeedStatus = FeedStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def mark_processed(self) -> DeliveryFeed:
        """配信済みステータスの新しいインスタンスを返します。"""
        return replace(self, status=FeedStatus.PROCESSED)

    def mark_failed(self) -> DeliveryFeed:
        """配信失敗ステータスの新しいインスタンスを返します。"""
        return replace(self, status=FeedStatus.FAILED)

    def with_sequence_id(self, sequence_id: SequenceId) -> DeliveryFeed:
        """シーケンスIDが付与された新しいインスタンスを返します。"""
        return replace(self, sequence_id=sequence_id)
