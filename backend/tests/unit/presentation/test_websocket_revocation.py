"""WebSocket 強制切断機能のユニットテスト。"""

import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.primitives.primitives import AuthToken, SessionId, UserId
from app.infrastructure.messaging.redis_subscriber import redis_subscriber
from app.presentation.websockets.manager import ChatManager


def _make_ws() -> MagicMock:
    ws = MagicMock()
    ws.accept = AsyncMock()
    ws.close = AsyncMock()
    from starlette.websockets import WebSocketState

    ws.application_state = WebSocketState.CONNECTED
    return ws


@pytest.fixture
def user_id() -> UserId:
    """テスト用のユーザーIDフィクスチャ。"""
    return UserId(uuid.uuid7())


class TestWebSocketRevocation:
    """WebSocket強制切断に関するテストクラス。"""

    async def test_force_disconnect_user_closes_websocket(
        self, user_id: UserId
    ) -> None:
        """force_disconnect_user はユーザーのすべての WebSocket をクローズし、

        切断処理を行う。
        """
        manager = ChatManager()
        ws1 = _make_ws()
        ws2 = _make_ws()

        await manager.connect(user_id, "alice", ws1)
        await manager.connect(user_id, "alice", ws2)

        assert manager.is_user_connected(user_id) is True

        await manager.force_disconnect_user(user_id)

        # 双方のソケットに対してクローズコード 1008 が呼び出されたことを検証
        ws1.close.assert_awaited_once_with(code=1008, reason="session_revoked")
        ws2.close.assert_awaited_once_with(code=1008, reason="session_revoked")

        # ユーザーが接続中リストから消えていることを検証
        assert manager.is_user_connected(user_id) is False

    async def test_force_disconnect_session_closes_only_target_session(
        self, user_id: UserId
    ) -> None:
        """force_disconnect_session は指定セッションの WebSocket のみをクローズし、

        同一ユーザーの別セッションの接続は維持される。
        """
        manager = ChatManager()
        session_a = SessionId(uuid.uuid7())
        session_b = SessionId(uuid.uuid7())
        ws_a = _make_ws()
        ws_b = _make_ws()

        await manager.connect(user_id, "alice", ws_a, session_a)
        await manager.connect(user_id, "alice", ws_b, session_b)

        await manager.force_disconnect_session(user_id, session_a)

        # session_a の接続だけがクローズされる
        ws_a.close.assert_awaited_once_with(code=1008, reason="session_revoked")
        ws_b.close.assert_not_awaited()

        # session_b の接続はユーザーが接続中のまま残る
        assert manager.is_user_connected(user_id) is True

    async def test_redis_subscriber_handles_force_disconnect(
        self, user_id: UserId
    ) -> None:
        """redis_subscriber が session_control チャネルから

        force_disconnect メッセージを受信した際、
        ConnectionManager の force_disconnect_user を呼び出す。
        """
        connection_manager = MagicMock()
        connection_manager.force_disconnect_user = AsyncMock()
        feed_router = MagicMock()

        # Redis クライアントのモック設定
        mock_pubsub = AsyncMock()

        # pubsub.listen() で制御用チャネルメッセージを1つ配信し、
        # ループを抜けるために例外を投げる
        class ExitLoop(BaseException):
            pass

        async def mock_listen():
            yield {
                "type": "message",
                "channel": b"session_control",
                "data": json.dumps(
                    {
                        "type": "force_disconnect",
                        "user_id": str(user_id.value),
                    }
                ),
            }
            raise ExitLoop("Exit loop for test")

        mock_pubsub.listen = mock_listen
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = MagicMock()

        mock_redis_client = MagicMock()
        mock_redis_client.pubsub.return_value = mock_pubsub
        mock_redis_client.close = AsyncMock()

        with patch("redis.asyncio.from_url", return_value=mock_redis_client):
            try:
                await redis_subscriber(connection_manager, feed_router)
            except ExitLoop:
                pass

        # 双方のチャネルが購読されたことの検証
        mock_pubsub.subscribe.assert_awaited_once_with("chat", "session_control")
        # connection_manager.force_disconnect_user が
        # 正しいユーザーIDで呼び出されたことの検証
        connection_manager.force_disconnect_user.assert_awaited_once_with(user_id)

    async def test_redis_subscriber_handles_force_disconnect_with_session_id(
        self, user_id: UserId
    ) -> None:
        """force_disconnect イベントに session_id が含まれる場合、

        ConnectionManager の force_disconnect_session（ユーザー全断ではなく
        セッション単位の切断）が呼び出される。
        """
        connection_manager = MagicMock()
        connection_manager.force_disconnect_session = AsyncMock()
        connection_manager.force_disconnect_user = AsyncMock()
        feed_router = MagicMock()

        session_id = SessionId(uuid.uuid7())
        mock_pubsub = AsyncMock()

        class ExitLoop(BaseException):
            pass

        async def mock_listen():
            yield {
                "type": "message",
                "channel": b"session_control",
                "data": json.dumps(
                    {
                        "type": "force_disconnect",
                        "user_id": str(user_id.value),
                        "session_id": str(session_id.value),
                    }
                ),
            }
            raise ExitLoop("Exit loop for test")

        mock_pubsub.listen = mock_listen
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = MagicMock()

        mock_redis_client = MagicMock()
        mock_redis_client.pubsub.return_value = mock_pubsub
        mock_redis_client.close = AsyncMock()

        with patch("redis.asyncio.from_url", return_value=mock_redis_client):
            try:
                await redis_subscriber(connection_manager, feed_router)
            except ExitLoop:
                pass

        connection_manager.force_disconnect_session.assert_awaited_once_with(
            user_id, session_id
        )
        connection_manager.force_disconnect_user.assert_not_awaited()

    async def test_auth_service_is_session_valid(self) -> None:
        """is_session_valid がデータベース上のセッション存在有無と有効期限を
        正しく判定することを検証。
        """
        # Mock UOW and JWT
        mock_uow = MagicMock()
        mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
        mock_uow.__aexit__ = AsyncMock(return_value=None)
        mock_jwt = MagicMock()

        token = AuthToken("mock_access_token")
        session_id = uuid.uuid7()
        mock_jwt.get_session_id_from_token.return_value = session_id

        from datetime import datetime, timedelta, timezone

        from app.application.services.auth_service import AuthService
        from app.domain.entities.refresh_token import RefreshToken as RefreshTokenEntity

        service = AuthService(mock_uow, mock_jwt, MagicMock(), 7)

        # ケース1: DBにセッションが見つからない -> False を返す
        mock_uow.refresh_tokens.get_by_id = AsyncMock(return_value=None)
        assert await service.is_session_valid(token) is False

        # ケース2: DBにセッションがあるが有効期限切れ -> False を返す
        expired_token = RefreshTokenEntity.create(
            id=SessionId(session_id),
            user_id=UserId(uuid.uuid7()),
            token_value="expired_refresh_token",
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
        )
        mock_uow.refresh_tokens.get_by_id = AsyncMock(return_value=expired_token)
        assert await service.is_session_valid(token) is False

        # ケース3: DBにセッションがあり有効期限内 -> True を返す
        valid_token = RefreshTokenEntity.create(
            id=SessionId(session_id),
            user_id=UserId(uuid.uuid7()),
            token_value="valid_refresh_token",
            expires_at=datetime.now(timezone.utc) + timedelta(days=5),
            created_at=datetime.now(timezone.utc),
        )
        mock_uow.refresh_tokens.get_by_id = AsyncMock(return_value=valid_token)
        assert await service.is_session_valid(token) is True

    async def test_reconnect_user_closes_websocket_with_1000(
        self, user_id: UserId
    ) -> None:
        """reconnect_user はユーザーのすべての WebSocket を
        クローズコード 1000 でクローズし、切断処理を行う。
        """
        manager = ChatManager()
        ws1 = _make_ws()
        ws2 = _make_ws()

        await manager.connect(user_id, "alice", ws1)
        await manager.connect(user_id, "alice", ws2)

        assert manager.is_user_connected(user_id) is True

        await manager.reconnect_user(user_id)

        # 双方のソケットに対してクローズコード 1000 が呼び出されたことを検証
        ws1.close.assert_awaited_once_with(code=1000, reason="reconnect")
        ws2.close.assert_awaited_once_with(code=1000, reason="reconnect")

        # ユーザーが接続中リストから消えていることを検証
        assert manager.is_user_connected(user_id) is False

    async def test_redis_subscriber_handles_reconnect(self, user_id: UserId) -> None:
        """redis_subscriber が session_control チャネルから
        reconnect メッセージを受信した際、
        ConnectionManager の reconnect_user を呼び出す。
        """
        connection_manager = MagicMock()
        connection_manager.reconnect_user = AsyncMock()
        feed_router = MagicMock()

        # Redis クライアントのモック設定
        mock_pubsub = AsyncMock()

        # pubsub.listen() で制御用チャネルメッセージを1つ配信し、
        # ループを抜けるために例外を投げる
        class ExitLoop(BaseException):
            pass

        async def mock_listen():
            yield {
                "type": "message",
                "channel": b"session_control",
                "data": json.dumps(
                    {
                        "type": "reconnect",
                        "user_id": str(user_id.value),
                    }
                ),
            }
            raise ExitLoop("Exit loop for test")

        mock_pubsub.listen = mock_listen
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = MagicMock()

        mock_redis_client = MagicMock()
        mock_redis_client.pubsub.return_value = mock_pubsub
        mock_redis_client.close = AsyncMock()

        with patch("redis.asyncio.from_url", return_value=mock_redis_client):
            try:
                await redis_subscriber(connection_manager, feed_router)
            except ExitLoop:
                pass

        # 双方のチャネルが購読されたことの検証
        mock_pubsub.subscribe.assert_awaited_once_with("chat", "session_control")
        # connection_manager.reconnect_user が
        # 正しいユーザーIDで呼び出されたことの検証
        connection_manager.reconnect_user.assert_awaited_once_with(user_id)
