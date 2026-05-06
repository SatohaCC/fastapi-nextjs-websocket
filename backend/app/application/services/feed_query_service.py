"""フィードの検索に関するユースケースを実現するアプリケーションサービス。"""

from ...domain.entities.delivery_feed import DeliveryFeed
from ..uow import UnitOfWork


class FeedQueryService:
    """フィード取得に関するユースケースをまとめたサービス。"""

    def __init__(self, uow: UnitOfWork) -> None:
        """FeedQueryService を初期化します。"""
        self._uow = uow

    async def get_feeds_after(
        self, sequence_name: str, after_id: int, username: str
    ) -> list[DeliveryFeed]:
        """指定したID以降の、ユーザーに関連するフィードを取得します。"""
        async with self._uow:
            return await self._uow.outbox.get_after(sequence_name, after_id, username)
