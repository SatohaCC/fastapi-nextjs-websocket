"""テスト全体で共有するフィクスチャ定義。"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.domain.entities.message import Message
from app.domain.primitives.primitives import EntityId, MessageText, Username


@pytest.fixture
def mock_uow():
    """DB 不要の UnitOfWork モック。async with / commit / rollback に対応。"""
    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.messages = AsyncMock()
    uow.requests = AsyncMock()
    uow.outbox = AsyncMock()
    return uow


@pytest.fixture
def saved_message():
    """テスト用の永続化済み Message エンティティ。"""
    return Message(
        id=EntityId(1),
        username=Username("alice"),
        text=MessageText("hello"),
        created_at=datetime.now(timezone.utc),
    )
