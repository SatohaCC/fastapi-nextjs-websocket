"""WebSocket 接続の管理とリアルタイム配信を担うクラス。"""

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from fastapi import WebSocket, WebSocketDisconnect

from ...domain.primitives.primitives import Username
from ...infrastructure.config import settings
from .schemas import (
    BaseServerMessage,
    create_server_message_from_feed,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class ChatManager:
    """WebSocket 接続の管理と、クライアントへのリアルタイム配信を担当するクラス。"""

    def __init__(self) -> None:
        """ChatManager を初期化します。"""
        # ユーザーをキー、そのユーザーの接続（複数可）のセットを値として保持
        self.connections: dict[Username, set[WebSocket]] = {}

    async def connect(self, username: Username, websocket: WebSocket) -> None:
        """新しい WebSocket 接続を受け入れ、管理リストに追加します。"""
        await websocket.accept()
        ws_id = id(websocket)
        logger.info("connect: user=%s ws=%d", username.value, ws_id)

        if username not in self.connections:
            self.connections[username] = set()
        self.connections[username].add(websocket)

        active_users = [u.value for u in self.connections.keys()]
        logger.debug(
            "active connections: user=%s count=%d total_users=%s",
            username.value,
            len(self.connections[username]),
            active_users,
        )

    def disconnect(
        self, websocket: WebSocket, username: Username | None = None
    ) -> None:
        """指定された WebSocket 接続を管理リストから削除します。"""
        ws_id = id(websocket)
        actual_user: Username | str = "unknown"

        if username and username in self.connections:
            if websocket in self.connections[username]:
                self.connections[username].discard(websocket)
                actual_user = username
            if not self.connections[username]:
                del self.connections[username]
        else:
            for user, ws_set in list(self.connections.items()):
                if websocket in ws_set:
                    ws_set.discard(websocket)
                    actual_user = user
                    if not ws_set:
                        del self.connections[user]
                    break

        user_str = (
            actual_user.value if isinstance(actual_user, Username) else actual_user
        )
        logger.info(
            "disconnect: user=%s ws=%d remaining_users=%s",
            user_str,
            ws_id,
            [u.value for u in self.connections.keys()],
        )

    async def send_to_user(self, username: Username, payload: Any) -> None:
        """特定のユーザーにのみデータを送信します。
        ユーザーが複数のデバイス（タブ）で接続している場合、すべてに送信されます。
        """
        # presentation → application の循環インポートを避けるため関数内でインポート
        from ...application.outbox.delivery_feed import DeliveryFeed

        if isinstance(payload, DeliveryFeed):
            dto = create_server_message_from_feed(payload)
            data = dto.model_dump(mode="json")
        elif isinstance(payload, BaseServerMessage):
            data = payload.model_dump(mode="json")
        else:
            data = payload

        if username not in self.connections:
            return

        ws_set = self.connections[username]

        # 非同期送信タスクのリストを作成
        tasks = []
        for ws in ws_set:
            tasks.append(self._send_safe(ws, data, username))

        if tasks:
            await asyncio.gather(*tasks)

    async def broadcast(self, payload: Any) -> None:
        """現在接続しているすべてのクライアントにデータを一斉送信します。"""
        # presentation → application の循環インポートを避けるため関数内でインポート
        from ...application.outbox.delivery_feed import DeliveryFeed

        if isinstance(payload, DeliveryFeed):
            dto = create_server_message_from_feed(payload)
            data = dto.model_dump(mode="json")
        elif isinstance(payload, BaseServerMessage):
            data = payload.model_dump(mode="json")
        else:
            data = payload

        tasks = []
        for user, ws_set in list(self.connections.items()):
            for ws in ws_set:
                tasks.append(self._send_safe(ws, data, user))

        if tasks:
            await asyncio.gather(*tasks)

    async def _send_safe(
        self, ws: WebSocket, payload: dict, username: Username | None = None
    ) -> None:
        """内部用の安全な送信メソッド。"""
        user_str = username.value if username else "unknown"
        try:
            await ws.send_json(payload)
        except WebSocketDisconnect as e:
            # Starlette は OSError も WebSocketDisconnect(code=1006) に変換する。
            logger.info(
                "send_safe disconnect: user=%s code=%s reason=%r",
                user_str,
                e.code,
                e.reason,
            )
            self.disconnect(ws, username)
        except RuntimeError as e:
            # state 違反等 (例: 既に close 済みの ws へ send)。
            logger.warning("send_safe runtime error: user=%s err=%s", user_str, e)
            self.disconnect(ws, username)


# シングルトンインスタンス
_manager = ChatManager()


def get_manager() -> ChatManager:
    """ChatManager のシングルトンインスタンスを取得します。"""
    return _manager


async def heartbeat(websocket: WebSocket, pong_event: asyncio.Event) -> None:
    """WebSocket 接続の死活監視を行うコルーチン。
    一定間隔で ping を送信し、制限時間内に pong が返ってこない場合は切断します。
    """
    while True:
        await asyncio.sleep(settings.PING_INTERVAL)
        pong_event.clear()
        try:
            await websocket.send_json({"type": "ping"})
        except WebSocketDisconnect as e:
            logger.info(
                "heartbeat ping failed, peer disconnected: code=%s reason=%r",
                e.code,
                e.reason,
            )
            _manager.disconnect(websocket)
            break
        except RuntimeError as e:
            logger.warning("heartbeat ping failed, runtime error: %s", e)
            _manager.disconnect(websocket)
            break
        try:
            await asyncio.wait_for(pong_event.wait(), timeout=settings.PONG_TIMEOUT)
        except asyncio.TimeoutError:
            logger.info("heartbeat timeout: closing connection")
            try:
                await websocket.close(code=1001, reason="pong timeout")
            except RuntimeError:
                pass
            _manager.disconnect(websocket)
            break
