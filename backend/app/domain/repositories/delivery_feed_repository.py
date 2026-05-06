"""DeliveryFeed リポジトリのインターフェース。"""

from typing import Protocol

from ..entities.delivery_feed import DeliveryFeed


class DeliveryFeedRepository(Protocol):
    """DeliveryFeed エンティティに対するデータアクセスのインターフェース。"""

    async def save(self, feed: DeliveryFeed) -> DeliveryFeed:
        """フィードを保存します。この際、厳密連番の採番も行われます。"""

    async def get_pending(self, limit: int = 100) -> list[DeliveryFeed]:
        """未配信（PENDING）のフィードを取得します。
        FOR UPDATE SKIP LOCKED を使用します。
        """

    async def mark_published(self, feed_keys: list[tuple[str, int]]) -> None:
        """指定されたフィードのステータスを PUBLISHED に更新します。"""

    async def get_after(
        self, sequence_name: str, after_id: int, username: str | None = None
    ) -> list[DeliveryFeed]:
        """指定された ID 以降のフィードを取得します。リカバリ用途です。"""

    async def delete_old_published_feeds(self, hours: int = 24) -> int:
        """指定された時間以上経過した PUBLISHED ステータスのフィードを削除します。"""
