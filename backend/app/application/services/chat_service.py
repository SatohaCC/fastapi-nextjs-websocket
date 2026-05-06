"""チャットメッセージに関するユースケースを実現するアプリケーションサービス。"""

from datetime import datetime, timezone

from ...domain.entities.delivery_feed import DeliveryFeed
from ...domain.entities.message import Message
from ...domain.factories.delivery_feed_factory import DeliveryFeedFactory
from ...domain.primitives.primitives import EntityId, MessageText, Username
from ..uow import UnitOfWork


class ChatService:
    """チャットに関するユースケースをまとめたアプリケーションサービス。"""

    def __init__(self, uow: UnitOfWork) -> None:
        """チャットサービスを初期化します。"""
        self._uow = uow

    async def send_message(self, username: str, text: str) -> Message:
        """メッセージを生成・保存し、パブリッシュします。"""
        message = Message(username=Username(username), text=MessageText(text))
        async with self._uow:
            saved_message = await self._uow.messages.save(message)

            # Outbox への保存（採番と記録）
            event_type, payload = DeliveryFeedFactory.create_payload_from_message(
                saved_message
            )

            feed = DeliveryFeed(
                sequence_name="chat_global",
                event_type=event_type,
                payload=payload,
                created_at=datetime.now(timezone.utc),
            )
            await self._uow.outbox.save(feed)

            await self._uow.commit()

        return saved_message

    async def get_messages_after(self, after_id: int) -> list[Message]:
        """指定したID以降のメッセージを取得します。"""
        async with self._uow:
            return await self._uow.messages.get_after(EntityId(after_id))

    async def get_recent_messages(self, limit: int = 50) -> list[Message]:
        """最新のメッセージを取得します。"""
        async with self._uow:
            return await self._uow.messages.get_recent(limit)
