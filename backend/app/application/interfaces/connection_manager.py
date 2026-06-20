"""WebSocket 接続管理を抽象化するインターフェース。"""

from typing import Any, Protocol

from ...domain.primitives.primitives import SessionId, UserId


class ConnectionManager(Protocol):
    """ユーザーへの接続管理とデータ配信を抽象化するインターフェース。
    チャットメッセージ、リクエスト通知、システム通知など、
    リアルタイムでクライアントに届けるべきあらゆるペイロードを扱います。
    """

    async def send_to_user(self, user_id: UserId, payload: Any) -> None:
        """指定したユーザーに対して、リアルタイムでデータを送信します。

        Args:
            user_id (UserId): 送信先のユーザー ID。
            payload (Any): 送信するドメインオブジェクト（DeliveryFeed等）。
                プレゼンテーション層の実装において DTO へ変換されます。
        """
        ...

    async def broadcast(self, payload: Any) -> None:
        """現在接続しているすべてのユーザーにデータを一斉配信します。

        Args:
            payload (Any): 配信するドメインオブジェクト。
        """
        ...

    async def force_disconnect_user(self, user_id: UserId) -> None:
        """指定されたユーザーのすべての WebSocket 接続を強制的にクローズします。"""
        ...

    async def force_disconnect_session(
        self, user_id: UserId, session_id: SessionId
    ) -> None:
        """指定されたユーザーのうち、特定セッションに紐づく WebSocket 接続のみを
        強制的にクローズします。
        """
        ...

    async def reconnect_user(self, user_id: UserId) -> None:
        """指定されたユーザーのすべての WebSocket 接続を切断し、再接続を促します。"""
        ...
