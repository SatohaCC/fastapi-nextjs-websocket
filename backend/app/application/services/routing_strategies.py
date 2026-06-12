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
    """feed が属する 1 ユーザーの inbox にのみ配信する戦略。

    DM は受信者ごとの inbox（``direct_request:{username}``）へ fan-out 保存され、
    各 feed は単一ユーザー宛になる。配信時は ``sequence_name`` から所有者
    username を取り出し、payload の sender / recipient と突き合わせてその
    ユーザーの ``user_id`` を解決し、その 1 人にだけ送る。
    """

    async def route(
        self,
        feed: "DeliveryFeed",
        connection_manager: ConnectionManager,
    ) -> None:
        """sequence_name が示す 1 ユーザーにのみ送信します。"""
        from ..outbox.delivery_feed import DIRECT_REQUEST_SEQUENCE_PREFIX
        from ..outbox.payload import DirectRequestPayload, DirectRequestUpdatePayload

        payload = feed.payload
        if not isinstance(payload, (DirectRequestPayload, DirectRequestUpdatePayload)):
            return

        sequence_name = feed.sequence_name.value
        if not sequence_name.startswith(DIRECT_REQUEST_SEQUENCE_PREFIX):
            return
        owner = sequence_name[len(DIRECT_REQUEST_SEQUENCE_PREFIX) :]

        # inbox 所有者が sender / recipient のどちらかを判定し、その user_id へ送る。
        target_id: UserId | None = None
        if owner == payload.sender.value:
            target_id = payload.sender_id
        elif owner == payload.recipient.value:
            target_id = payload.recipient_id

        if target_id:
            await connection_manager.send_to_user(target_id, feed)
