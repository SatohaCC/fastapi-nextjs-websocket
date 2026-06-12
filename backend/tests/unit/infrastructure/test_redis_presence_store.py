"""RedisPresenceStore のユニットテスト（redis をモック化）。

接続ごとの TTL 付きエントリ（ソート済み集合）による add/remove のオンライン
遷移判定と、期限切れ掃除（reap）を伴うロスター取得を検証する。
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.infrastructure.messaging.redis_presence_store import RedisPresenceStore


def _store_with_mock() -> tuple[RedisPresenceStore, MagicMock]:
    mock_redis = MagicMock()
    mock_redis.zadd = AsyncMock()
    mock_redis.zrem = AsyncMock()
    mock_redis.zcard = AsyncMock()
    mock_redis.zrange = AsyncMock()
    mock_redis.zremrangebyscore = AsyncMock()
    mock_redis.expire = AsyncMock()
    mock_redis.delete = AsyncMock()
    with patch("redis.asyncio.from_url", return_value=mock_redis):
        store = RedisPresenceStore("redis://localhost:6379")
    return store, mock_redis


@pytest.mark.asyncio
async def test_add_connection_first_marks_online() -> None:
    """初接続（既存接続 0）でオンラインとなり True を返す。"""
    store, r = _store_with_mock()
    r.zcard.return_value = 0  # reap 後の現存接続数
    became = await store.add_connection("alice", "c1")
    assert became is True
    # 接続集合とロスターの両方へ追加する（score=deadline は時刻依存なのでキーで検証）。
    assert r.zadd.await_count == 2
    zadd_keys = {call.args[0] for call in r.zadd.await_args_list}
    assert zadd_keys == {"presence:conns:alice", "presence:online"}
    # conn_id / username が member として登録されている。
    conns_call = next(
        c for c in r.zadd.await_args_list if c.args[0] == "presence:conns:alice"
    )
    assert "c1" in conns_call.args[1]
    r.zremrangebyscore.assert_awaited()  # 先に期限切れを掃除している
    r.expire.assert_awaited()  # キー自体にも TTL を張る


@pytest.mark.asyncio
async def test_add_connection_second_not_online() -> None:
    """2 本目以降（既存接続あり）はオンライン遷移せず False を返す。"""
    store, r = _store_with_mock()
    r.zcard.return_value = 1
    became = await store.add_connection("alice", "c2")
    assert became is False


@pytest.mark.asyncio
async def test_remove_connection_last_marks_offline() -> None:
    """最後の接続（残り 0）でオフライン化し True を返す。"""
    store, r = _store_with_mock()
    r.zcard.return_value = 0
    became = await store.remove_connection("alice", "c1")
    assert became is True
    r.zrem.assert_any_await("presence:conns:alice", "c1")
    r.delete.assert_awaited_once_with("presence:conns:alice")
    r.zrem.assert_any_await("presence:online", "alice")


@pytest.mark.asyncio
async def test_remove_connection_not_last() -> None:
    """まだ接続が残る（残り>0）場合はオフライン化せず False を返す。"""
    store, r = _store_with_mock()
    r.zcard.return_value = 1
    became = await store.remove_connection("alice", "c1")
    assert became is False
    r.delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_refresh_connection_extends_deadline() -> None:
    """Refresh で接続集合・ロスター・キー TTL を延長する。"""
    store, r = _store_with_mock()
    await store.refresh_connection("alice", "c1")
    assert r.zadd.await_count == 2  # 接続集合 + ロスター
    r.expire.assert_awaited_once()


@pytest.mark.asyncio
async def test_online_usernames_reaps_then_sorts_and_decodes() -> None:
    """先に期限切れを掃除し、残ったロスターを bytes デコード・ソートして返す。"""
    store, r = _store_with_mock()
    r.zrange.return_value = [b"charlie", b"alice", b"bob"]
    result = await store.online_usernames()
    assert result == ["alice", "bob", "charlie"]
    r.zremrangebyscore.assert_awaited_once()  # reap してから取得
