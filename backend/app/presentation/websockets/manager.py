"""WebSocket 接続の管理とリアルタイム配信を担うクラス。"""

import asyncio

from fastapi import WebSocket, WebSocketDisconnect

from ...infrastructure.config import settings


class ChatManager:
    """WebSocket 接続の管理と、クライアントへのリアルタイム配信を担当するクラス。"""

    def __init__(self) -> None:
        """ChatManager を初期化します。"""
        # ユーザー名をキー、そのユーザーの接続（複数可）のセットを値として保持
        self.connections: dict[str, set[WebSocket]] = {}

    async def connect(self, username: str, websocket: WebSocket) -> None:
        """新しい WebSocket 接続を受け入れ、管理リストに追加します。"""
        await websocket.accept()
        ws_id = id(websocket)
        print(f"[connect] {username} (ws:{ws_id}) が入室完了")

        if username not in self.connections:
            self.connections[username] = set()
        self.connections[username].add(websocket)

        active_users = list(self.connections.keys())
        print(
            f"DEBUG: {username} connections: {len(self.connections[username])} | Total users: {active_users}"
        )

    def disconnect(self, websocket: WebSocket, username: str | None = None) -> None:
        """指定された WebSocket 接続を管理リストから削除します。"""
        ws_id = id(websocket)
        actual_user = "unknown"

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

        print(
            f"[disconnect] {actual_user} (ws:{ws_id}) が退室 | 残りユーザー: {list(self.connections.keys())}"
        )

    async def send_to_user(self, username: str, payload: dict) -> None:
        """特定のユーザーにのみデータを送信します。
        ユーザーが複数のデバイス（タブ）で接続している場合、すべてに送信されます。
        """
        if username not in self.connections:
            return

        ws_set = self.connections[username]

        # 非同期送信タスクのリストを作成
        tasks = []
        for ws in ws_set:
            tasks.append(self._send_safe(ws, payload, username))

        if tasks:
            await asyncio.gather(*tasks)

    async def broadcast(self, payload: dict) -> None:
        """現在接続しているすべてのクライアントにデータを一斉送信します。"""
        tasks = []
        for username, ws_set in list(self.connections.items()):
            for ws in ws_set:
                tasks.append(self._send_safe(ws, payload, username))

        if tasks:
            await asyncio.gather(*tasks)

    async def _send_safe(
        self, ws: WebSocket, payload: dict, username: str | None = None
    ) -> None:
        """内部用の安全な送信メソッド。"""
        try:
            await ws.send_json(payload)
        except (WebSocketDisconnect, RuntimeError):
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
        except (WebSocketDisconnect, RuntimeError):
            _manager.disconnect(websocket)
            break
        try:
            await asyncio.wait_for(pong_event.wait(), timeout=settings.PONG_TIMEOUT)
        except asyncio.TimeoutError:
            print("[timeout] pong が返らなかったため切断")
            try:
                await websocket.close(code=1001, reason="pong timeout")
            except RuntimeError:
                pass
            _manager.disconnect(websocket)
            break
