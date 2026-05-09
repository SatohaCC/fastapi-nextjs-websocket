"""チャットメッセージに関するユースケースを実現するアプリケーションサービス。"""

from ...domain.entities.message import DraftMessage, Message
from ...domain.primitives.primitives import EntityId, MessageText, Username
from ..outbox.delivery_feed import CHAT_SEQUENCE, DraftDeliveryFeed
from ..outbox.payload import MessagePayload
from ..uow import UnitOfWork


class ChatService:
    """チャットに関するユースケースをまとめたアプリケーションサービス。"""

    def __init__(self, uow: UnitOfWork) -> None:
        """チャットサービスを初期化します。"""
        self._uow = uow

    async def send_message(self, username: Username, text: MessageText) -> Message:
        """メッセージを生成・保存し、パブリッシュします。"""
        draft = DraftMessage(username=username, text=text)
        async with self._uow:
            saved_message = await self._uow.messages.save(draft)
            payload = MessagePayload(
                id=saved_message.id,
                username=saved_message.username,
                text=saved_message.text,
                created_at=saved_message.created_at,
            )
            feed = DraftDeliveryFeed(
                sequence_name=CHAT_SEQUENCE,
                event_type=payload.event_type,
                payload=payload,
            )
            await self._uow.outbox.save(feed)
            await self._uow.commit()

        return saved_message

    async def get_messages_after(self, after_id: EntityId) -> list[Message]:
        """指定したID以降のメッセージを取得します。"""
        async with self._uow:
            return await self._uow.messages.get_after(after_id)

    async def get_recent_messages(self, limit: int = 50) -> list[Message]:
        """最新のメッセージを取得します。"""
        async with self._uow:
            return await self._uow.messages.get_recent(limit)
