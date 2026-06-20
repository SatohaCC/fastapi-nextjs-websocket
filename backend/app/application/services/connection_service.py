"""WebSocket 接続のライフサイクルに関するアプリケーションサービス。"""

from ...domain.primitives.feed import FeedEventType
from ...domain.primitives.primitives import Username
from ..outbox.delivery_feed import SYSTEM_SEQUENCE, DraftDeliveryFeed
from ..outbox.payload import SystemEventPayload
from ..uow import UnitOfWork


class ConnectionService:
    """WebSocket 接続のライフサイクルに関連するアプリケーションサービス。

    入室・退室時のイベントを Transactional Outbox に記録し、
    RelayWorker 経由で配信します。
    これにより、チャット・リクエストと同じ信頼性の高い配信経路を使用します。
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """接続サービスを初期化します。

        Args:
            uow: トランザクション境界を管理する UnitOfWork。
        """
        self._uow = uow

    async def handle_user_join(self, username: Username) -> None:
        """ユーザーが入室した際の処理。Outbox にイベントを記録します。"""
        payload = SystemEventPayload(type=FeedEventType.JOIN, username=username)
        feed = DraftDeliveryFeed(
            sequence_name=SYSTEM_SEQUENCE,
            event_type=payload.event_type,
            payload=payload,
        )
        async with self._uow:
            await self._uow.outbox.save(feed)
            await self._uow.commit()

    async def handle_user_leave(self, username: Username) -> None:
        """ユーザーが退室した際の処理。Outbox にイベントを記録します。"""
        payload = SystemEventPayload(type=FeedEventType.LEAVE, username=username)
        feed = DraftDeliveryFeed(
            sequence_name=SYSTEM_SEQUENCE,
            event_type=payload.event_type,
            payload=payload,
        )
        async with self._uow:
            await self._uow.outbox.save(feed)
            await self._uow.commit()
