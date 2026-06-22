"""差分復旧の穴検知と永続テーブルフォールバックのユニットテスト。

24h クリーンアップで Outbox の古い区間が消えた状態で、古い cursor を持つ
クライアントが再接続したとき、永続テーブル（messages/tasks）の recent で補填する
挙動を検証する。
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.outbox.delivery_feed import SequenceName
from app.presentation.websockets.endpoint import (
    _send_initial_data,
    has_recovery_hole,
)


class TestHasRecoveryHole:
    """has_recovery_hole の純粋ロジックを検証する。"""

    def test_no_data_no_hole(self) -> None:
        """Head が None（ストリーム空）なら穴なし。"""
        assert has_recovery_hole(500, None, None) is False

    def test_cursor_at_head_no_hole(self) -> None:
        """Cursor が head 以上（新規データ無し）なら穴なし。"""
        assert has_recovery_hole(500, 1, 500) is False
        assert has_recovery_hole(500, 1, 499) is False

    def test_contiguous_no_hole(self) -> None:
        """Cursor 直後（min_retained == cursor+1）が残っていれば穴なし。"""
        assert has_recovery_hole(500, 501, 1000) is False

    def test_cursor_points_at_retained_no_hole(self) -> None:
        """Cursor の seq 自体が保持されていれば穴なし。"""
        assert has_recovery_hole(500, 500, 1000) is False

    def test_pruned_below_cursor_is_hole(self) -> None:
        """Cursor 直後が削除済み（min_retained > cursor+1）なら穴あり。"""
        assert has_recovery_hole(500, 502, 1000) is True
        assert has_recovery_hole(500, 850, 1000) is True

    def test_all_pruned_is_hole(self) -> None:
        """全削除済み（min_retained None）かつ head>cursor なら穴あり。"""
        assert has_recovery_hole(500, None, 1000) is True


class _FakeResp:
    def __init__(self, item: object) -> None:
        self.item = item

    def model_dump(self, mode: str) -> dict[str, object]:
        return {"item": self.item, "mode": mode}


class _FakeModel:
    @classmethod
    def from_domain(cls, item: object, is_history: bool = False) -> _FakeResp:
        return _FakeResp(item)


def _make_feed_service(
    bounds: tuple[int | None, int | None], feeds: list[object]
) -> MagicMock:
    svc = MagicMock()
    svc.get_sequence_bounds = AsyncMock(return_value=bounds)
    svc.get_feeds_after = AsyncMock(return_value=feeds)
    return svc


class TestSendInitialDataFallback:
    """_send_initial_data の穴フォールバック挙動を検証する。"""

    async def test_hole_triggers_durable_fallback(self) -> None:
        """穴がある場合、history_fetcher（永続テーブル）を呼んで補填送信する。"""
        ws = MagicMock()
        ws.send_json = AsyncMock()
        history_fetcher = AsyncMock(return_value=["msg-a", "msg-b"])
        # bounds: min_retained=850 (501..849 削除済み), head=1000 → 穴あり
        feed_service = _make_feed_service((850, 1000), [])

        await _send_initial_data(
            websocket=ws,
            user=MagicMock(),
            last_id=500,
            sequence_name=SequenceName("global_chat"),
            feed_service=feed_service,
            history_fetcher=history_fetcher,
            response_model=_FakeModel,  # type: ignore[arg-type]
        )

        history_fetcher.assert_awaited_once()
        # 永続の2件が送信されている
        assert ws.send_json.await_count == 2

    async def test_no_hole_skips_durable_fallback(self) -> None:
        """穴が無ければ history_fetcher を呼ばず、Outbox 差分のみ送る。"""
        ws = MagicMock()
        ws.send_json = AsyncMock()
        history_fetcher = AsyncMock(return_value=["should-not-send"])
        # bounds: min_retained=501 (連続), head=1000 → 穴なし
        feed_service = _make_feed_service((501, 1000), [])

        await _send_initial_data(
            websocket=ws,
            user=MagicMock(),
            last_id=500,
            sequence_name=SequenceName("global_chat"),
            feed_service=feed_service,
            history_fetcher=history_fetcher,
            response_model=_FakeModel,  # type: ignore[arg-type]
        )

        history_fetcher.assert_not_awaited()

    async def test_initial_load_without_cursor_uses_history(self) -> None:
        """Cursor 無し（last_id=None）は従来どおり永続履歴を送る。"""
        ws = MagicMock()
        ws.send_json = AsyncMock()
        history_fetcher = AsyncMock(return_value=["h1", "h2", "h3"])
        feed_service = _make_feed_service((None, None), [])

        await _send_initial_data(
            websocket=ws,
            user=MagicMock(),
            last_id=None,
            sequence_name=SequenceName("global_chat"),
            feed_service=feed_service,
            history_fetcher=history_fetcher,
            response_model=_FakeModel,  # type: ignore[arg-type]
        )

        history_fetcher.assert_awaited_once()
        assert ws.send_json.await_count == 3
        # cursor 無しでは bounds 照会はしない
        feed_service.get_sequence_bounds.assert_not_called()


@pytest.mark.parametrize(
    ("last_id", "min_retained", "head", "expected"),
    [
        (0, 1, 10, False),
        (0, None, 0, False),
        (0, None, 10, True),
        (5, 8, 10, True),
        (5, 6, 10, False),
    ],
)
def test_has_recovery_hole_param(
    last_id: int, min_retained: int | None, head: int | None, expected: bool
) -> None:
    """has_recovery_hole の代表ケースを表で検証する。"""
    assert has_recovery_hole(last_id, min_retained, head) is expected
