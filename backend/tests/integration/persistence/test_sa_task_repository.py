"""SqlAlchemyTaskRepository の統合テスト。"""

from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.task import DraftTask, Task
from app.domain.primitives.primitives import TaskText, UserId, Username
from app.domain.primitives.task_status import TaskStatus
from app.infrastructure.persistence.sa_task_repository import (
    SqlAlchemyTaskRepository,
)


@pytest.fixture
def repo(db_session: AsyncSession):
    """リポジトリのフィクスチャ。"""
    return SqlAlchemyTaskRepository(db_session)


@pytest.mark.asyncio
async def test_save_new_task(
    repo: SqlAlchemyTaskRepository, seeded_users: dict[str, UserId]
):
    """新規 Task を保存し、ID が採番されることを確認。"""
    alice_id = seeded_users["alice"]
    bob_id = seeded_users["bob"]
    draft = DraftTask(
        sender_id=alice_id,
        recipient_id=bob_id,
        sender=Username("alice"),
        recipient=Username("bob"),
        text=TaskText("help me"),
        status=TaskStatus.REQUESTED,
        created_at=datetime.now(timezone.utc),
    )

    saved = await repo.save(draft)

    assert saved.id.value > 0
    assert saved.status == TaskStatus.REQUESTED
    assert saved.sender_id == alice_id
    assert saved.recipient_id == bob_id
    assert saved.sender == draft.sender


@pytest.mark.asyncio
async def test_update_existing_task(
    repo: SqlAlchemyTaskRepository, seeded_users: dict[str, UserId]
):
    """既存の Task の状態を更新（保存）できることを確認。"""
    alice_id = seeded_users["alice"]
    bob_id = seeded_users["bob"]
    # 1. 新規作成
    draft = DraftTask(
        sender_id=alice_id,
        recipient_id=bob_id,
        sender=Username("alice"),
        recipient=Username("bob"),
        text=TaskText("initial"),
        status=TaskStatus.REQUESTED,
        created_at=datetime.now(timezone.utc),
    )
    saved = await repo.save(draft)

    # 2. 更新
    updated_draft = Task(
        id=saved.id,
        sender_id=saved.sender_id,
        recipient_id=saved.recipient_id,
        sender=saved.sender,
        recipient=saved.recipient,
        text=saved.text,
        status=TaskStatus.PROCESSING,
        created_at=saved.created_at,
        updated_at=datetime.now(timezone.utc),
    )

    final = await repo.save(updated_draft)

    assert final.id == saved.id
    assert final.status == TaskStatus.PROCESSING


@pytest.mark.asyncio
async def test_get_for_user_returns_both_sent_and_received(
    repo: SqlAlchemyTaskRepository, seeded_users: dict[str, UserId]
):
    """ユーザーが送信・受信した Task を両方取得できることを確認。"""
    alice_id = seeded_users["alice"]
    bob_id = seeded_users["bob"]
    charlie_id = seeded_users["charlie"]

    # Alice から Bob
    await repo.save(
        DraftTask(
            sender_id=alice_id,
            recipient_id=bob_id,
            sender=Username("alice"),
            recipient=Username("bob"),
            text=TaskText("msg1"),
            status=TaskStatus.REQUESTED,
            created_at=datetime.now(timezone.utc),
        )
    )
    # Bob から Alice
    await repo.save(
        DraftTask(
            sender_id=bob_id,
            recipient_id=alice_id,
            sender=Username("bob"),
            recipient=Username("alice"),
            text=TaskText("msg2"),
            status=TaskStatus.REQUESTED,
            created_at=datetime.now(timezone.utc),
        )
    )
    # Charlie から Bob (Alice 無関係)
    await repo.save(
        DraftTask(
            sender_id=charlie_id,
            recipient_id=bob_id,
            sender=Username("charlie"),
            recipient=Username("bob"),
            text=TaskText("msg3"),
            status=TaskStatus.REQUESTED,
            created_at=datetime.now(timezone.utc),
        )
    )

    alice_tasks = await repo.get_for_user(alice_id)

    assert len(alice_tasks) == 2
    assert {t.text.value for t in alice_tasks} == {"msg1", "msg2"}
