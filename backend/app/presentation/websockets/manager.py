"""WebSocket 接続の管理とリアルタイム配信を担うクラス。"""

import asyncio
import json
import logging
from typing import TYPE_CHECKING, Any

from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from ...domain.primitives.primitives import UserId
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
        self.connections: dict[UserId, set[WebSocket]] = {}
        # 在席ロスター用の UserId → username マッピング。
        # ユーザーの最後の接続が切れた時点で削除する。
        self._usernames: dict[UserId, str] = {}

    async def connect(
        self, user_id: UserId, username: str, websocket: WebSocket
    ) -> bool:
        """新しい WebSocket 接続を受け入れ、管理リストに追加します。

        Returns:
            このユーザーにとって初めてのアクティブな接続（0→1 への遷移）
            であれば ``True``。プレゼンス（入室通知）の対称性を保つために
            呼び出し側が JOIN 配信の要否を判断するのに使う。
        """
        await websocket.accept()
        ws_id = id(websocket)
        logger.info("connect: user=%s ws=%d", user_id.value, ws_id)

        is_first_connection = user_id not in self.connections
        if is_first_connection:
            self.connections[user_id] = set()
        self.connections[user_id].add(websocket)
        self._usernames[user_id] = username

        active_users = [u.value for u in self.connections.keys()]
        logger.debug(
            "active connections: user=%s count=%d total_users=%s",
            user_id.value,
            len(self.connections[user_id]),
            active_users,
        )
        return is_first_connection

    def is_user_connected(self, user_id: UserId) -> bool:
        """指定ユーザーにアクティブな接続が残っているかを返します。"""
        return user_id in self.connections

    def online_usernames(self) -> list[str]:
        """現在アクティブな接続を持つユーザー名の一覧を返します（在席ロスター）。"""
        return sorted(
            self._usernames[uid] for uid in self.connections if uid in self._usernames
        )

    def disconnect(self, websocket: WebSocket, user_id: UserId | None = None) -> None:
        """指定された WebSocket 接続を管理リストから削除します。"""
        ws_id = id(websocket)
        actual_user: UserId | str = "unknown"

        if user_id and user_id in self.connections:
            if websocket in self.connections[user_id]:
                self.connections[user_id].discard(websocket)
                actual_user = user_id
            if not self.connections[user_id]:
                del self.connections[user_id]
                self._usernames.pop(user_id, None)
        else:
            for user, ws_set in list(self.connections.items()):
                if websocket in ws_set:
                    ws_set.discard(websocket)
                    actual_user = user
                    if not ws_set:
                        del self.connections[user]
                        self._usernames.pop(user, None)
                    break

        user_str = actual_user.value if isinstance(actual_user, UserId) else actual_user
        logger.info(
            "disconnect: user=%s ws=%d remaining_users=%s",
            user_str,
            ws_id,
            [u.value for u in self.connections.keys()],
        )

    @staticmethod
    def _serialize(payload: Any) -> str:
        """Payload を 1 回だけ JSON 文字列化する。

        ``broadcast`` のように複数の WS へ同じ payload を送る場合に、
        Pydantic ``model_dump_json`` を 1 回呼ぶだけで済むようにする。
        Starlette の ``send_text`` はバイト化のみ行う。
        """
        # presentation → application の循環インポートを避けるため関数内でインポート
        from ...application.outbox.delivery_feed import DeliveryFeed

        if isinstance(payload, DeliveryFeed):
            return create_server_message_from_feed(payload).model_dump_json()
        if isinstance(payload, BaseServerMessage):
            return payload.model_dump_json()
        # dict などのフォールバック (Starlette と同じ separators / ensure_ascii)
        return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)

    async def send_to_user(self, user_id: UserId, payload: Any) -> None:
        """特定のユーザーにのみデータを送信します。
        ユーザーが複数のデバイス（タブ）で接続している場合、すべてに送信されます。
        """
        if user_id not in self.connections:
            logger.debug(
                "send_to_user: user %s is not connected. Skipping.",
                user_id.value,
            )
            return

        text = self._serialize(payload)
        ws_set = self.connections[user_id]
        logger.debug(
            "send_to_user: user %s has %d connections. Sending...",
            user_id.value,
            len(ws_set),
        )

        tasks = [self._send_safe(ws, text, user_id) for ws in ws_set]
        if tasks:
            await asyncio.gather(*tasks)

    async def broadcast(self, payload: Any) -> None:
        """現在接続しているすべてのクライアントにデータを一斉送信します。"""
        text = self._serialize(payload)
        active_users = [u.value for u in self.connections.keys()]
        logger.debug(
            "broadcast: current active users: %s",
            active_users,
        )

        tasks = [
            self._send_safe(ws, text, user)
            for user, ws_set in list(self.connections.items())
            for ws in ws_set
        ]
        if tasks:
            logger.debug(
                "broadcasting to %d active sockets...",
                len(tasks),
            )
            await asyncio.gather(*tasks)

    async def _send_safe(
        self, ws: WebSocket, text: str, user_id: UserId | None = None
    ) -> None:
        """内部用の安全な送信メソッド。

        ``text`` は事前にシリアライズ済みの JSON 文字列であることを前提とする。
        """
        user_str = str(user_id.value) if user_id else "unknown"
        # 既に close 済みの socket への送信を未然に skip し、例外ノイズを減らす。
        # 例外ベースの cleanup は維持しているため、これは最適化目的のみ。
        if ws.application_state != WebSocketState.CONNECTED:
            logger.debug(
                "send_safe skip: user=%s state=%s", user_str, ws.application_state
            )
            self.disconnect(ws, user_id)
            return
        try:
            logger.debug(
                "send_safe: sending message to user %s",
                user_str,
            )
            await ws.send_text(text)
            logger.debug(
                "send_safe: successfully sent to user %s",
                user_str,
            )
        except WebSocketDisconnect as e:
            # Starlette は OSError も WebSocketDisconnect(code=1006) に変換する。
            logger.info(
                "send_safe disconnect: user=%s code=%s reason=%r",
                user_str,
                e.code,
                e.reason,
            )
            self.disconnect(ws, user_id)
        except RuntimeError as e:
            # state 違反等 (例: 既に close 済みの ws へ send)。
            logger.warning("send_safe runtime error: user=%s err=%s", user_str, e)
            self.disconnect(ws, user_id)


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
