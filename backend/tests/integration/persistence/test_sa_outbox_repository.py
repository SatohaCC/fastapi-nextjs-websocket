"""SqlAlchemyDeliveryFeedRepository の統合テスト。"""

from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.outbox.delivery_feed import (
    DraftDeliveryFeed,
    FeedStatus,
    SequenceId,
    SequenceName,
)
from app.application.outbox.payload import (
    MessagePayload,
    RequestPayload,
    SystemEventPayload,
)
from app.domain.primitives.feed import FeedEventType
from app.domain.primitives.primitives import (
    EntityId,
    MessageText,
    RequestText,
    Username,
)
from app.domain.primitives.request_status import RequestStatus
from app.infrastructure.persistence.sa_outbox_repository import (
    SqlAlchemyDeliveryFeedRepository,
)


@pytest.fixture
def repo(db_session: AsyncSession):
    """リポジトリのフィクスチャ。"""
    return SqlAlchemyDeliveryFeedRepository(db_session)


@pytest.mark.asyncio
async def test_save_increments_sequence_id(repo: SqlAlchemyDeliveryFeedRepository):
    """保存時にシーケンス ID が 1 から順にインクリメントされることを確認。"""
    seq_name = SequenceName("test_seq")
    payload = SystemEventPayload(type=FeedEventType.JOIN, username=Username("alice"))

    # 1回目
    feed1 = await repo.save(
        DraftDeliveryFeed(
            sequence_name=seq_name, event_type=FeedEventType.JOIN, payload=payload
        )
    )
    # 2回目
    feed2 = await repo.save(
        DraftDeliveryFeed(
            sequence_name=seq_name, event_type=FeedEventType.JOIN, payload=payload
        )
    )

    assert feed1.sequence_id.value == 1
    assert feed2.sequence_id.value == 2
    assert feed1.sequence_name == seq_name


@pytest.mark.asyncio
async def test_get_pending_and_mark_processed(repo: SqlAlchemyDeliveryFeedRepository):
    """PENDING 状態のフィードを取得し、処理済みとしてマークできることを確認。"""
    seq_name = SequenceName("test_seq")
    payload = SystemEventPayload(type=FeedEventType.JOIN, username=Username("alice"))

    await repo.save(
        DraftDeliveryFeed(
            sequence_name=seq_name, event_type=FeedEventType.JOIN, payload=payload
        )
    )

    # 未処理分を取得
    pending = await repo.get_pending(limit=10)
    assert len(pending) == 1
    assert pending[0].status == FeedStatus.PENDING

    # 処理済みに更新
    await repo.mark_processed([(pending[0].sequence_name, pending[0].sequence_id)])

    # 再度取得（空のはず）
    pending_after = await repo.get_pending(limit=10)
    assert len(pending_after) == 0


@pytest.mark.asyncio
async def test_get_after_filtering(repo: SqlAlchemyDeliveryFeedRepository):
    """指定した ID 以降のフィードを取得できることを確認。
    ユーザー名によるフィルタリングも含めて検証します。
    """
    seq_name = SequenceName("test_seq")

    # 全体向けメッセージ
    await repo.save(
        DraftDeliveryFeed(
            sequence_name=seq_name,
            event_type=FeedEventType.MESSAGE,
            payload=MessagePayload(
                id=EntityId(1),
                username=Username("alice"),
                text=MessageText("hello"),
                created_at=datetime.now(timezone.utc),
            ),
        )
    )
    # Bob へのリクエスト
    await repo.save(
        DraftDeliveryFeed(
            sequence_name=seq_name,
            event_type=FeedEventType.REQUEST,
            payload=RequestPayload(
                id=EntityId(2),
                sender=Username("charlie"),
                recipient=Username("bob"),
                text=RequestText("hey"),
                status=RequestStatus.REQUESTED,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
        )
    )

    # Alice 関連（全体メッセージが含まれる）
    alice_feeds = await repo.get_after(
        seq_name, SequenceId(0), username=Username("alice")
    )
    assert len(alice_feeds) == 1

    # Bob 関連（全体メッセージ + Bob へのリクエスト）
    bob_feeds = await repo.get_after(seq_name, SequenceId(0), username=Username("bob"))
    assert len(bob_feeds) == 2
