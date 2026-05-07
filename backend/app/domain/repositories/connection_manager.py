"""WebSocket 接続管理を抽象化するリポジトリインターフェース。"""

from typing import Any, Protocol

from ...domain.primitives.primitives import Username


class ConnectionManager(Protocol):
    """ユーザーへの接続管理とデータ配信を抽象化するインターフェース。
    チャットメッセージ、リクエスト通知、システム通知など、
    リアルタイムでクライアントに届けるべきあらゆるペイロードを扱います。
    """

    async def send_to_user(self, username: Username, payload: dict[str, Any]) -> None:
        """指定したユーザーに対して、リアルタイムでデータを送信します。

        Args:
            username (Username): 送信先のユーザー名。
            payload (dict): 送信するデータ。
                type フィールドによってクライアント側で処理が振り分けられます。
        """

    async def broadcast(self, payload: dict[str, Any]) -> None:
        """現在接続しているすべてのユーザーにデータを一斉配信します。

        Args:
            payload (dict): 配信するデータ。
        """
