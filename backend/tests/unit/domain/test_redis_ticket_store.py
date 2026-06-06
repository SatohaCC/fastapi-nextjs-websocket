"""RedisTicketStore のユニットテスト。"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.primitives.primitives import UserId
from app.infrastructure.auth.redis_ticket_store import RedisTicketStore
from app.infrastructure.auth.uuid7 import generate_uuid7

TEST_UUID = generate_uuid7()
TEST_USER_ID = UserId(TEST_UUID)


@pytest.mark.asyncio
async def test_redis_ticket_store_lifecycle() -> None:
    """チケットの生成と検証（ワンタイム消費）のテスト。"""
    mock_redis = MagicMock()
    mock_redis.set = AsyncMock()
    mock_redis.getdel = AsyncMock(return_value=str(TEST_UUID).encode("utf-8"))

    with patch("redis.asyncio.from_url", return_value=mock_redis):
        store = RedisTicketStore("redis://localhost:6379")

        # 1. チケットの生成
        ticket = await store.create_ticket(TEST_USER_ID)

        assert ticket.startswith("ws_ticket_")
        mock_redis.set.assert_called_once()
        args, kwargs = mock_redis.set.call_args
        assert args[0] == ticket
        assert args[1] == str(TEST_UUID)
        assert kwargs["ex"] == 10

        # 2. チケットの消費（成功）
        consumed_user_id = await store.consume_ticket(ticket)
        assert consumed_user_id == TEST_USER_ID
        mock_redis.getdel.assert_called_once_with(ticket)

        # 3. チケットの消費（存在しない場合）
        mock_redis.getdel.reset_mock()
        mock_redis.getdel.return_value = None

        not_found = await store.consume_ticket("invalid_ticket")
        assert not_found is None
        mock_redis.getdel.assert_called_once_with("invalid_ticket")
