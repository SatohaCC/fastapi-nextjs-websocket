from typing import Awaitable, Callable

from ...domain.primitives.primitives import Username


class ConnectionService:
    """WebSocket 接続のライフサイクルに関連するアプリケーションサービス。
    入室・退室時のイベント発行などを担当します。

    join/leave は transient なイベントのため、delivery_feeds には記録せず
    Redis へ直接パブリッシュします。
    """

    def __init__(self, publish: Callable[[dict], Awaitable[None]]) -> None:
        """接続サービスを初期化します。

        Args:
            publish: Redis へイベントをパブリッシュするコールバック。
        """
        self._publish = publish

    async def handle_user_join(self, username: Username) -> None:
        """ユーザーが入室した際の処理。"""
        await self._publish({"type": "join", "username": username.value})

    async def handle_user_leave(self, username: Username) -> None:
        """ユーザーが退室した際の処理。"""
        await self._publish({"type": "leave", "username": username.value})
