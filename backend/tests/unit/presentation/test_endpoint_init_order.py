"""WebSocket 初期化の順序不変条件をテストで固定する。

データロスト対策として、``ws_manager.connect``（socket をロスターへ登録）は
``_send_initial_data``（履歴スナップショット取得）より **前** に行う必要がある。

この順序により、登録後にブロードキャストされたメッセージは live で届き、
スナップショットはその時点までを含むため、両者は「重複（overlap）」となり
取りこぼし（gap）が生じない。クライアントは id で重複排除する。
この順序が崩れると、登録前のブロードキャストが live にもスナップショットにも
含まれない穴になりうる。
"""

from unittest.mock import AsyncMock, MagicMock

from app.presentation.websockets.endpoint import websocket_endpoint


class _StopInit(Exception):
    """スナップショット取得まで到達した時点で初期化を早期終了させる番兵例外。"""


async def test_socket_registered_before_snapshot() -> None:
    """connect（登録）が get_recent_messages（スナップショット）より先に呼ばれる。"""
    order: list[str] = []

    websocket = MagicMock()
    websocket.send_json = AsyncMock()
    websocket.close = AsyncMock()

    user = MagicMock()
    user.username.value = "alice"

    ws_manager = MagicMock()

    async def _connect(_uid: object, _uname: object, _sock: object) -> bool:
        order.append("register")
        return True

    ws_manager.connect = AsyncMock(side_effect=_connect)
    ws_manager.disconnect = MagicMock()
    ws_manager.online_usernames = MagicMock(return_value=[])
    ws_manager.is_user_connected = MagicMock(return_value=False)

    global_chat_service = MagicMock()

    async def _recent() -> list[object]:
        order.append("snapshot")
        # ここまでの順序だけ確認できればよいので、初期化を早期終了させる。
        # endpoint の except Exception で捕捉され、関数は正常 return する。
        raise _StopInit

    global_chat_service.get_recent_messages = AsyncMock(side_effect=_recent)

    # 在席ストア（クラスタ共有）。init 失敗時も外側の finally で remove される。
    presence_store = MagicMock()
    presence_store.add_connection = AsyncMock(return_value=True)
    presence_store.remove_connection = AsyncMock(return_value=False)
    presence_store.refresh_connection = AsyncMock()
    presence_store.online_usernames = AsyncMock(return_value=[])

    # 以降は到達しないが、シグネチャを満たすためのモック。
    direct_request_service = MagicMock()
    feed_service = MagicMock()
    connection_service = MagicMock()
    connection_service.handle_user_join = AsyncMock()
    connection_service.handle_user_leave = AsyncMock()
    rate_limiter = MagicMock()

    # _StopInit は endpoint 内で捕捉され、例外は外に出ない（正常 return）。
    await websocket_endpoint(
        websocket=websocket,
        user=user,
        global_chat_service=global_chat_service,
        direct_request_service=direct_request_service,
        feed_service=feed_service,
        connection_service=connection_service,
        ws_manager=ws_manager,
        presence_store=presence_store,
        chat_message_rate_limiter=rate_limiter,
        direct_request_rate_limiter=rate_limiter,
        status_update_rate_limiter=rate_limiter,
        last_chat_id=None,
        last_request_id=None,
    )

    # 登録 → スナップショットの順で呼ばれていること。
    assert order == ["register", "snapshot"]
    ws_manager.connect.assert_awaited_once()
