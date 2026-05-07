"""配信フィードのルーティング戦略の具象実装。"""

from typing import Any

from ...domain.primitives.primitives import Username
from ...domain.repositories.connection_manager import ConnectionManager


class BroadcastStrategy:
    """全クライアントに一斉配信する戦略。

    チャットメッセージや入退室イベントなど、
    すべてのユーザーに通知すべきイベントに使用します。
    """

    async def route(
        self,
        payload: dict[str, Any],
        connection_manager: ConnectionManager,
    ) -> None:
        """全クライアントにブロードキャストします。"""
        await connection_manager.broadcast(payload)


class DirectStrategy:
    """送信者と受信者のみに配信する戦略。

    ダイレクトリクエストなど、関係者のみに通知すべきイベントに使用します。
    """

    async def route(
        self,
        payload: dict[str, Any],
        connection_manager: ConnectionManager,
    ) -> None:
        """Sender と recipient にのみ送信します。"""
        sender_str = payload.get("sender")
        recipient_str = payload.get("recipient")

        if sender_str:
            await connection_manager.send_to_user(Username(sender_str), payload)
        if recipient_str and recipient_str != sender_str:
            await connection_manager.send_to_user(Username(recipient_str), payload)
