"""フィード取得に関するユースケースを実現するアプリケーションサービス。"""

from ...domain.primitives.primitives import Userid
from ..outbox.delivery_feed import DeliveryFeed, SequenceId, SequenceName
from ..uow import UnitOfWork


class FeedQueryService:
    """フィード取得に関するユースケースをまとめたサービス。"""

    def __init__(self, uow: UnitOfWork) -> None:
        """FeedQueryService を初期化します。"""
        self._uow = uow

    async def get_feeds_after(
        self,
        sequence_name: SequenceName,
        after_id: SequenceId,
        userid: Userid,
    ) -> list[DeliveryFeed]:
        """指定したID以降の、ユーザーに関連するフィードを取得します。"""
        async with self._uow:
            return await self._uow.outbox.get_after(sequence_name, after_id, userid)

    async def get_sequence_bounds(
        self, sequence_name: SequenceName
    ) -> tuple[int | None, int | None]:
        """``(保持中の最小 sequence_id, 採番済みの最大 sequence_id)`` を返します。

        リカバリ時に、クライアントの cursor が 24h クリーンアップで削除された区間
        （穴）を指していないか判定するために使用します。
        """
        async with self._uow:
            return await self._uow.outbox.get_sequence_bounds(sequence_name)
