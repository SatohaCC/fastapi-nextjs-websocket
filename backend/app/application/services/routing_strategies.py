"""配信フィードのルーティング戦略の具象実装。"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..outbox.delivery_feed import DeliveryFeed

from ...domain.primitives.primitives import UserId
from ..interfaces.connection_manager import ConnectionManager


class BroadcastStrategy:
    """全クライアントに一斉配信する戦略。

    チャットメッセージや入退室イベントなど、
    すべてのユーザーに通知すべきイベントに使用します。
    """

    async def route(
        self,
        feed: "DeliveryFeed",
        connection_manager: ConnectionManager,
    ) -> None:
        """全クライアントにブロードキャストします。"""
        await connection_manager.broadcast(feed)


class DirectStrategy:
    """送信者と受信者のみに配信する戦略。

    ダイレクトリクエストなど、関係者のみに通知すべきイベントに使用します。
    """

    async def route(
        self,
        feed: "DeliveryFeed",
        connection_manager: ConnectionManager,
    ) -> None:
        """Sender と recipient にのみ送信します。"""
        from ..outbox.payload import DirectRequestPayload, DirectRequestUpdatePayload

        payload = feed.payload
        sender_id: UserId | None = None
        recipient_id: UserId | None = None

        if isinstance(payload, (DirectRequestPayload, DirectRequestUpdatePayload)):
            sender_id = payload.sender_id
            recipient_id = payload.recipient_id

        if sender_id:
            await connection_manager.send_to_user(sender_id, feed)
        if recipient_id and recipient_id != sender_id:
            await connection_manager.send_to_user(recipient_id, feed)
