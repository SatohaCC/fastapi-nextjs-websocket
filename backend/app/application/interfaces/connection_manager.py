"""WebSocket 接続管理を抽象化するインターフェース。"""

from typing import Any, Protocol

from ...domain.primitives.primitives import Username


class ConnectionManager(Protocol):
    """ユーザーへの接続管理とデータ配信を抽象化するインターフェース。
    チャットメッセージ、リクエスト通知、システム通知など、
    リアルタイムでクライアントに届けるべきあらゆるペイロードを扱います。
    """

    async def send_to_user(self, username: Username, payload: Any) -> None:
        """指定したユーザーに対して、リアルタイムでデータを送信します。

        Args:
            username (Username): 送信先のユーザー名。
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
