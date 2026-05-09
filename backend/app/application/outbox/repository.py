"""Outbox リポジトリのインターフェース定義。"""

from typing import Protocol

from ...domain.primitives.primitives import Username
from .delivery_feed import DeliveryFeed, DraftDeliveryFeed, SequenceId, SequenceName


class DeliveryFeedRepository(Protocol):
    """DeliveryFeed エンティティに対するデータアクセスのインターフェース。"""

    async def save(self, feed: DraftDeliveryFeed) -> DeliveryFeed:
        """DraftDeliveryFeed を永続化し、採番済みの DeliveryFeed を返します。"""
        ...

    async def get_pending(self, limit: int = 100) -> list[DeliveryFeed]:
        """未配信（PENDING）のフィードを取得します。
        FOR UPDATE SKIP LOCKED を使用します。
        """
        ...

    async def mark_processed(
        self, feed_keys: list[tuple[SequenceName, SequenceId]]
    ) -> None:
        """指定されたフィードのステータスを PROCESSED に更新します。"""
        ...

    async def get_after(
        self,
        sequence_name: SequenceName,
        after_id: SequenceId,
        username: Username | None = None,
    ) -> list[DeliveryFeed]:
        """指定された ID 以降のフィードを取得します。リカバリ用途です。"""
        ...

    async def delete_old_processed_feeds(self, hours: int = 24) -> int:
        """指定された時間以上経過した PROCESSED ステータスのフィードを削除します。"""
        ...
