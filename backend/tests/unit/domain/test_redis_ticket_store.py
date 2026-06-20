"""RedisTicketStore のユニットテスト。"""

import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.primitives.primitives import SessionId, UserId
from app.infrastructure.auth.redis_ticket_store import RedisTicketStore

TEST_UUID = uuid.uuid7()
TEST_USER_ID = UserId(TEST_UUID)
TEST_SESSION_UUID = uuid.uuid7()
TEST_SESSION_ID = SessionId(TEST_SESSION_UUID)


@pytest.mark.asyncio
async def test_redis_ticket_store_lifecycle() -> None:
    """チケットの生成と検証（ワンタイム消費）のテスト。session_id も保持される。"""
    mock_redis = MagicMock()
    mock_redis.set = AsyncMock()
    mock_redis.getdel = AsyncMock(
        return_value=json.dumps(
            {"user_id": str(TEST_UUID), "session_id": str(TEST_SESSION_UUID)}
        ).encode("utf-8")
    )

    with patch("redis.asyncio.from_url", return_value=mock_redis):
        store = RedisTicketStore("redis://localhost:6379")

        # 1. チケットの生成
        ticket = await store.create_ticket(TEST_USER_ID, TEST_SESSION_ID)

        assert ticket.startswith("ws_ticket_")
        mock_redis.set.assert_called_once()
        args, kwargs = mock_redis.set.call_args
        assert args[0] == ticket
        payload = json.loads(args[1])
        assert payload["user_id"] == str(TEST_UUID)
        assert payload["session_id"] == str(TEST_SESSION_UUID)
        assert kwargs["ex"] == 10

        # 2. チケットの消費（成功）
        consumed = await store.consume_ticket(ticket)
        assert consumed == (TEST_USER_ID, TEST_SESSION_ID)
        mock_redis.getdel.assert_called_once_with(ticket)

        # 3. チケットの消費（存在しない場合）
        mock_redis.getdel.reset_mock()
        mock_redis.getdel.return_value = None

        not_found = await store.consume_ticket("invalid_ticket")
        assert not_found is None
        mock_redis.getdel.assert_called_once_with("invalid_ticket")


@pytest.mark.asyncio
async def test_redis_ticket_store_without_session_id() -> None:
    """session_id を指定しない場合、None として保存・復元されることを検証。"""
    mock_redis = MagicMock()
    mock_redis.set = AsyncMock()
    mock_redis.getdel = AsyncMock(
        return_value=json.dumps({"user_id": str(TEST_UUID), "session_id": None}).encode(
            "utf-8"
        )
    )

    with patch("redis.asyncio.from_url", return_value=mock_redis):
        store = RedisTicketStore("redis://localhost:6379")

        ticket = await store.create_ticket(TEST_USER_ID)
        args, _ = mock_redis.set.call_args
        payload = json.loads(args[1])
        assert payload["session_id"] is None

        consumed = await store.consume_ticket(ticket)
        assert consumed == (TEST_USER_ID, None)
