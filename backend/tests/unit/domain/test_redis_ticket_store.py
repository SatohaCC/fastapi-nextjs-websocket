"""RedisTicketStore のユニットテスト。"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.primitives.primitives import Username
from app.infrastructure.auth.redis_ticket_store import RedisTicketStore


@pytest.mark.asyncio
async def test_redis_ticket_store_lifecycle() -> None:
    """チケットの生成と検証（ワンタイム消費）のテスト。"""
    mock_redis = MagicMock()
    mock_redis.set = AsyncMock()
    mock_redis.get = AsyncMock(return_value=b"alice")
    mock_redis.delete = AsyncMock()

    with patch("redis.asyncio.from_url", return_value=mock_redis):
        store = RedisTicketStore("redis://localhost:6379")

        # 1. チケットの生成
        username = Username("alice")
        ticket = await store.create_ticket(username)

        assert ticket.startswith("ws_ticket_")
        mock_redis.set.assert_called_once()
        args, kwargs = mock_redis.set.call_args
        assert args[0] == ticket
        assert args[1] == "alice"
        assert kwargs["ex"] == 10

        # 2. チケットの消費（成功）
        consumed_username = await store.consume_ticket(ticket)
        assert consumed_username == username
        mock_redis.get.assert_called_once_with(ticket)
        mock_redis.delete.assert_called_once_with(ticket)

        # 3. チケットの消費（存在しない場合）
        mock_redis.get.reset_mock()
        mock_redis.get.return_value = None
        mock_redis.delete.reset_mock()

        not_found_username = await store.consume_ticket("invalid_ticket")
        assert not_found_username is None
        mock_redis.get.assert_called_once_with("invalid_ticket")
        mock_redis.delete.assert_not_called()
