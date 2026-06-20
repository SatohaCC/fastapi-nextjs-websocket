"""ChatManager の接続数ベースのプレゼンス判定と在席ロスターのユニットテスト。

JOIN/LEAVE の対称性は接続数の 0→1 / →0 の遷移で判断される。
ここではその判定材料となる ``connect`` の戻り値・``is_user_connected``・
``online_usernames`` を検証する。
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.primitives.primitives import UserId
from app.presentation.websockets.manager import ChatManager


def _make_ws() -> MagicMock:
    """accept() のみ await される最小限の WebSocket スタブ。"""
    ws = MagicMock()
    ws.accept = AsyncMock()
    return ws


@pytest.fixture
def user_id() -> UserId:
    """テスト用のユーザー ID。"""
    return UserId(uuid.uuid7())


class TestChatManagerConnect:
    """ChatManager.connect の戻り値（初接続判定）を検証する。"""

    async def test_first_connection_returns_true(self, user_id: UserId) -> None:
        """ユーザーの最初の接続では True（0→1 遷移）を返す。"""
        manager = ChatManager()
        is_first = await manager.connect(user_id, "alice", _make_ws())
        assert is_first is True

    async def test_second_connection_returns_false(self, user_id: UserId) -> None:
        """同一ユーザーの 2 本目の接続では False を返す（多重タブ）。"""
        manager = ChatManager()
        await manager.connect(user_id, "alice", _make_ws())
        is_first = await manager.connect(user_id, "alice", _make_ws())
        assert is_first is False

    async def test_accepts_the_websocket(self, user_id: UserId) -> None:
        """Connect は WebSocket を accept する。"""
        manager = ChatManager()
        ws = _make_ws()
        await manager.connect(user_id, "alice", ws)
        ws.accept.assert_awaited_once()


class TestChatManagerPresence:
    """is_user_connected による退室判定（→0 遷移）を検証する。"""

    async def test_connected_after_connect(self, user_id: UserId) -> None:
        """接続後はアクティブ扱い。"""
        manager = ChatManager()
        await manager.connect(user_id, "alice", _make_ws())
        assert manager.is_user_connected(user_id) is True

    async def test_still_connected_while_other_tab_remains(
        self, user_id: UserId
    ) -> None:
        """2 タブ接続中に 1 本切断してもアクティブのまま（LEAVE を出さない）。"""
        manager = ChatManager()
        ws1 = _make_ws()
        ws2 = _make_ws()
        await manager.connect(user_id, "alice", ws1)
        await manager.connect(user_id, "alice", ws2)

        manager.disconnect(ws1, user_id)

        assert manager.is_user_connected(user_id) is True

    async def test_not_connected_after_last_disconnect(self, user_id: UserId) -> None:
        """最後の接続が切れたら非アクティブ（ここで LEAVE を出す）。"""
        manager = ChatManager()
        ws = _make_ws()
        await manager.connect(user_id, "alice", ws)

        manager.disconnect(ws, user_id)

        assert manager.is_user_connected(user_id) is False

    async def test_reconnect_after_full_disconnect_is_first_again(
        self, user_id: UserId
    ) -> None:
        """完全に切断した後の再接続は再び初接続（JOIN を出す）。"""
        manager = ChatManager()
        ws1 = _make_ws()
        await manager.connect(user_id, "alice", ws1)
        manager.disconnect(ws1, user_id)

        is_first = await manager.connect(user_id, "alice", _make_ws())

        assert is_first is True


class TestChatManagerRoster:
    """online_usernames による在席ロスターを検証する。"""

    async def test_empty_when_no_connections(self) -> None:
        """接続が無ければ空リスト。"""
        manager = ChatManager()
        assert manager.online_usernames() == []

    async def test_lists_connected_usernames_sorted(self) -> None:
        """接続中のユーザー名をソート済みで返す。"""
        manager = ChatManager()
        await manager.connect(UserId(uuid.uuid7()), "charlie", _make_ws())
        await manager.connect(UserId(uuid.uuid7()), "alice", _make_ws())
        await manager.connect(UserId(uuid.uuid7()), "bob", _make_ws())

        assert manager.online_usernames() == ["alice", "bob", "charlie"]

    async def test_username_deduplicated_across_tabs(self, user_id: UserId) -> None:
        """同一ユーザーが複数タブで接続してもロスターには 1 度だけ現れる。"""
        manager = ChatManager()
        await manager.connect(user_id, "alice", _make_ws())
        await manager.connect(user_id, "alice", _make_ws())

        assert manager.online_usernames() == ["alice"]

    async def test_username_removed_after_last_disconnect(
        self, user_id: UserId
    ) -> None:
        """最後の接続が切れたらロスターから消える。"""
        manager = ChatManager()
        ws = _make_ws()
        await manager.connect(user_id, "alice", ws)

        manager.disconnect(ws, user_id)

        assert manager.online_usernames() == []

    async def test_username_remains_while_other_tab_open(self, user_id: UserId) -> None:
        """1 タブ切断してももう一方が残っていればロスターに残る。"""
        manager = ChatManager()
        ws1 = _make_ws()
        ws2 = _make_ws()
        await manager.connect(user_id, "alice", ws1)
        await manager.connect(user_id, "alice", ws2)

        manager.disconnect(ws1, user_id)

        assert manager.online_usernames() == ["alice"]
