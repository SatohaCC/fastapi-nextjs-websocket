"""SqlAlchemyMessageRepository の統合テスト。"""

from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.message import DraftMessage
from app.domain.primitives.primitives import EntityId, MessageText, Username
from app.infrastructure.persistence.sa_message_repository import (
    SqlAlchemyMessageRepository,
)


@pytest.mark.asyncio
async def test_save_and_get_message(db_session: AsyncSession):
    """メッセージを保存し、ID で取得できることを確認。"""
    repo = SqlAlchemyMessageRepository(db_session)
    draft = DraftMessage(
        username=Username("alice"),
        text=MessageText("hello"),
        created_at=datetime.now(timezone.utc),
    )

    saved = await repo.save(draft)

    assert saved.id.value > 0
    assert saved.username == draft.username
    assert saved.text == draft.text


@pytest.mark.asyncio
async def test_get_after_returns_ordered_messages(db_session: AsyncSession):
    """指定した ID 以降のメッセージが正しい順序で取得できることを確認。"""
    repo = SqlAlchemyMessageRepository(db_session)

    # 3件保存
    for i in range(3):
        await repo.save(
            DraftMessage(
                username=Username(f"user{i}"),
                text=MessageText(f"msg{i}"),
                created_at=datetime.now(timezone.utc),
            )
        )

    # 全件取得して先頭の ID を特定
    all_msgs = await repo.get_after(EntityId(0))
    first_id = all_msgs[0].id

    # 2番目以降を取得
    after_msgs = await repo.get_after(first_id)

    assert len(after_msgs) == 2
    assert after_msgs[0].text.value == "msg1"
    assert after_msgs[1].text.value == "msg2"


@pytest.mark.asyncio
async def test_get_recent_limit(db_session: AsyncSession):
    """最新のメッセージが件数制限に従って取得できることを確認。"""
    repo = SqlAlchemyMessageRepository(db_session)

    # 5件保存
    for i in range(5):
        await repo.save(
            DraftMessage(
                username=Username("alice"),
                text=MessageText(f"msg{i}"),
                created_at=datetime.now(timezone.utc),
            )
        )

    recent = await repo.get_recent(limit=3)

    assert len(recent) == 3
    # 古い順に並んでいるはずなので、msg2, msg3, msg4 が期待値
    assert recent[0].text.value == "msg2"
    assert recent[1].text.value == "msg3"
    assert recent[2].text.value == "msg4"
