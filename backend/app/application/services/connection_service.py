"""WebSocket 接続のライフサイクルに関するアプリケーションサービス。"""

from ...domain.entities.delivery_feed import DraftDeliveryFeed
from ...domain.entities.system_event import SystemEvent
from ...domain.primitives.feed import FeedEventType, SequenceName
from ...domain.primitives.primitives import Username
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
        event = SystemEvent(type=FeedEventType.JOIN, username=username)
        payload = event.to_payload()

        feed = DraftDeliveryFeed(
            sequence_name=SequenceName("system_global"),
            event_type=payload.event_type,
            payload=payload,
        )
        async with self._uow:
            await self._uow.outbox.save(feed)
            await self._uow.commit()

    async def handle_user_leave(self, username: Username) -> None:
        """ユーザーが退室した際の処理。Outbox にイベントを記録します。"""
        event = SystemEvent(type=FeedEventType.LEAVE, username=username)
        payload = event.to_payload()

        feed = DraftDeliveryFeed(
            sequence_name=SequenceName("system_global"),
            event_type=payload.event_type,
            payload=payload,
        )
        async with self._uow:
            await self._uow.outbox.save(feed)
            await self._uow.commit()
