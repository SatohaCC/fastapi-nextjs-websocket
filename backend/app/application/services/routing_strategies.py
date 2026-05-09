"""配信フィードのルーティング戦略の具象実装。"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.delivery_feed import DeliveryFeed

from ...domain.primitives.primitives import Username
from ...domain.repositories.connection_manager import ConnectionManager


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
        from ...domain.entities.payload import RequestPayload, RequestUpdatePayload

        payload = feed.payload
        sender: Username | None = None
        recipient: Username | None = None

        if isinstance(payload, (RequestPayload, RequestUpdatePayload)):
            sender = payload.sender
            recipient = payload.recipient

        if sender:
            await connection_manager.send_to_user(sender, feed)
        if recipient and recipient != sender:
            await connection_manager.send_to_user(recipient, feed)
