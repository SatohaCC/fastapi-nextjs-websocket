"""Outbox リポジトリのインターフェース定義。"""

from typing import Protocol

from ...domain.primitives.primitives import Userid
from ..outbox.delivery_feed import (
    DeliveryFeed,
    DraftDeliveryFeed,
    SequenceId,
    SequenceName,
)


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
        userid: Userid | None = None,
        limit: int = 500,
    ) -> list[DeliveryFeed]:
        """指定された ID 以降のフィードを ``limit`` 件まで取得します（リカバリ用）。"""
        ...

    async def get_sequence_bounds(
        self, sequence_name: SequenceName
    ) -> tuple[int | None, int | None]:
        """リカバリの穴検知用の境界値を返します。

        ``(保持中の最小 sequence_id, 採番済みの最大 sequence_id)`` を返します。

        最小値は ``delivery_feeds`` に現存する最小 ``sequence_id``（24h クリーンアップで
        古い行が消えると上昇する）。最大値は当該シーケンス名に対応するネイティブ
        PostgreSQL SEQUENCE の ``nextval()`` 採番済みの最大値。いずれも該当が無ければ
        ``None``。
        """
        ...

    async def delete_old_processed_feeds(self, hours: int = 24) -> int:
        """指定された時間以上経過した PROCESSED ステータスのフィードを削除します。"""
        ...

    async def drop_sequence(self, sequence_name: SequenceName) -> None:
        """指定シーケンス名に対応するネイティブ SEQUENCE を削除します。

        ユーザー退会時など、per-user inbox（``direct_request:{userid}``）の
        後始末として呼び出される。
        """
        ...
