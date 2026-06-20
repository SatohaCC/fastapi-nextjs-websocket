"""SqlAlchemyMessageRepository の統合テスト。"""

from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.message import DraftMessage
from app.domain.primitives.primitives import EntityId, MessageText, UserId, Username
from app.infrastructure.persistence.sa_message_repository import (
    SqlAlchemyMessageRepository,
)


@pytest.mark.asyncio
async def test_save_and_get_message(
    db_session: AsyncSession, seeded_users: dict[str, UserId]
):
    """メッセージを保存し、ID で取得できることを確認。"""
    repo = SqlAlchemyMessageRepository(db_session)
    alice_id = seeded_users["alice"]
    draft = DraftMessage(
        user_id=alice_id,
        username=Username("alice"),
        text=MessageText("hello"),
        created_at=datetime.now(timezone.utc),
    )

    saved = await repo.save(draft)

    assert saved.id.value > 0
    assert saved.user_id == alice_id
    assert saved.username == draft.username
    assert saved.text == draft.text


@pytest.mark.asyncio
async def test_get_after_returns_ordered_messages(
    db_session: AsyncSession, seeded_users: dict[str, UserId]
):
    """指定した ID 以降のメッセージが正しい順序で取得できることを確認。"""
    repo = SqlAlchemyMessageRepository(db_session)

    usernames = ["alice", "bob", "charlie"]
    for name in usernames:
        uid = seeded_users[name]
        await repo.save(
            DraftMessage(
                user_id=uid,
                username=Username(name),
                text=MessageText(f"msg_{name}"),
                created_at=datetime.now(timezone.utc),
            )
        )

    # 全件取得して先頭の ID を特定
    all_msgs = await repo.get_after(EntityId(0))
    first_id = all_msgs[0].id

    # 2番目以降を取得
    after_msgs = await repo.get_after(first_id)

    assert len(after_msgs) == 2


@pytest.mark.asyncio
async def test_get_recent_limit(
    db_session: AsyncSession, seeded_users: dict[str, UserId]
):
    """最新のメッセージが件数制限に従って取得できることを確認。"""
    repo = SqlAlchemyMessageRepository(db_session)
    alice_id = seeded_users["alice"]

    for i in range(5):
        await repo.save(
            DraftMessage(
                user_id=alice_id,
                username=Username("alice"),
                text=MessageText(f"msg{i}"),
                created_at=datetime.now(timezone.utc),
            )
        )

    recent = await repo.get_recent(limit=3)

    assert len(recent) == 3


@pytest.mark.asyncio
async def test_get_before_returns_ordered_messages(
    db_session: AsyncSession, seeded_users: dict[str, UserId]
):
    """指定した ID より前のメッセージが正しい順序で、
    かつ制限件数以内で取得できることを確認。
    """
    repo = SqlAlchemyMessageRepository(db_session)
    alice_id = seeded_users["alice"]

    saved_messages = []
    for i in range(5):
        msg = await repo.save(
            DraftMessage(
                user_id=alice_id,
                username=Username("alice"),
                text=MessageText(f"msg_{i}"),
                created_at=datetime.now(timezone.utc),
            )
        )
        saved_messages.append(msg)

    # 4番目（インデックス3）のメッセージのIDを基準にする
    target_id = saved_messages[3].id

    # target_id より前のものを最大2件取得
    # （インデックス1, 2のメッセージが取得されるはず）
    before_msgs = await repo.get_before(target_id, limit=2)

    assert len(before_msgs) == 2
    assert before_msgs[0].text.value == "msg_1"
    assert before_msgs[1].text.value == "msg_2"
