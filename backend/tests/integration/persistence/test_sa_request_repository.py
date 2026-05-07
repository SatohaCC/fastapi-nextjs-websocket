"""SqlAlchemyRequestRepository の統合テスト。"""

from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.direct_request import DirectRequest, DraftDirectRequest
from app.domain.primitives.primitives import RequestText, Username
from app.domain.primitives.request_status import RequestStatus
from app.infrastructure.persistence.sa_request_repository import (
    SqlAlchemyRequestRepository,
)


@pytest.fixture
def repo(db_session: AsyncSession):
    """リポジトリのフィクスチャ。"""
    return SqlAlchemyRequestRepository(db_session)


@pytest.mark.asyncio
async def test_save_new_request(repo: SqlAlchemyRequestRepository):
    """新規リクエストを保存し、ID が採番されることを確認。"""
    draft = DraftDirectRequest(
        sender=Username("alice"),
        recipient=Username("bob"),
        text=RequestText("help me"),
        status=RequestStatus.REQUESTED,
        created_at=datetime.now(timezone.utc),
    )

    saved = await repo.save(draft)

    assert saved.id.value > 0
    assert saved.status == RequestStatus.REQUESTED
    assert saved.sender == draft.sender


@pytest.mark.asyncio
async def test_update_existing_request(repo: SqlAlchemyRequestRepository):
    """既存のリクエストの状態を更新（保存）できることを確認。"""
    # 1. 新規作成
    draft = DraftDirectRequest(
        sender=Username("alice"),
        recipient=Username("bob"),
        text=RequestText("initial"),
        status=RequestStatus.REQUESTED,
        created_at=datetime.now(timezone.utc),
    )
    saved = await repo.save(draft)

    # 2. 更新
    updated_draft = DirectRequest(
        id=saved.id,
        sender=saved.sender,
        recipient=saved.recipient,
        text=saved.text,
        status=RequestStatus.PROCESSING,
        created_at=saved.created_at,
        updated_at=datetime.now(timezone.utc),
    )

    final = await repo.save(updated_draft)

    assert final.id == saved.id
    assert final.status == RequestStatus.PROCESSING


@pytest.mark.asyncio
async def test_get_for_user_returns_both_sent_and_received(
    repo: SqlAlchemyRequestRepository,
):
    """ユーザーが送信・受信したリクエストを両方取得できることを確認。"""
    # Alice から Bob
    await repo.save(
        DraftDirectRequest(
            sender=Username("alice"),
            recipient=Username("bob"),
            text=RequestText("msg1"),
            status=RequestStatus.REQUESTED,
            created_at=datetime.now(timezone.utc),
        )
    )
    # Bob から Alice
    await repo.save(
        DraftDirectRequest(
            sender=Username("bob"),
            recipient=Username("alice"),
            text=RequestText("msg2"),
            status=RequestStatus.REQUESTED,
            created_at=datetime.now(timezone.utc),
        )
    )
    # Charlie から Bob (Alice 無関係)
    await repo.save(
        DraftDirectRequest(
            sender=Username("charlie"),
            recipient=Username("bob"),
            text=RequestText("msg3"),
            status=RequestStatus.REQUESTED,
            created_at=datetime.now(timezone.utc),
        )
    )

    alice_requests = await repo.get_for_user(Username("alice"))

    assert len(alice_requests) == 2
    assert {r.text.value for r in alice_requests} == {"msg1", "msg2"}
