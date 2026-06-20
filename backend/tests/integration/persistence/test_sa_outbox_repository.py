"""SqlAlchemyDeliveryFeedRepository の統合テスト。"""

from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.outbox.delivery_feed import (
    DraftDeliveryFeed,
    FeedStatus,
    SequenceId,
    SequenceName,
    direct_request_sequence,
)
from app.application.outbox.payload import (
    DirectRequestPayload,
    GlobalChatPayload,
    SystemEventPayload,
)
from app.domain.primitives.feed import FeedEventType
from app.domain.primitives.primitives import (
    EntityId,
    MessageText,
    TaskText,
    UserId,
    Userid,
    Username,
)
from app.domain.primitives.task_status import TaskStatus
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
async def test_get_after_filtering(
    repo: SqlAlchemyDeliveryFeedRepository, seeded_users: dict[str, UserId]
):
    """指定した ID 以隔のフィードを取得できることを確認。
    ユーザー名によるフィルタリングも含めて検証します。
    """
    seq_name = SequenceName("test_seq")
    charlie_id = seeded_users["charlie"]
    bob_id = seeded_users["bob"]

    # 全体向けメッセージ
    await repo.save(
        DraftDeliveryFeed(
            sequence_name=seq_name,
            event_type=FeedEventType.GLOBAL_CHAT,
            payload=GlobalChatPayload(
                id=EntityId(1),
                username=Username("alice"),
                text=MessageText("hello"),
                created_at=datetime.now(timezone.utc),
            ),
        )
    )
    # Bob へのダイレクトリクエスト
    await repo.save(
        DraftDeliveryFeed(
            sequence_name=seq_name,
            event_type=FeedEventType.DIRECT_REQUEST,
            payload=DirectRequestPayload(
                id=EntityId(2),
                sender_id=charlie_id,
                recipient_id=bob_id,
                sender_userid=Userid("charlie"),
                recipient_userid=Userid("bob"),
                sender=Username("charlie"),
                recipient=Username("bob"),
                text=TaskText("hey"),
                status=TaskStatus.REQUESTED,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
        )
    )

    # Alice 関連（全体メッセージが含まれる）
    alice_feeds = await repo.get_after(seq_name, SequenceId(0), userid=Userid("alice"))
    assert len(alice_feeds) == 1

    # Bob 関連（全体メッセージ + Bob へのリクエスト）
    bob_feeds = await repo.get_after(seq_name, SequenceId(0), userid=Userid("bob"))
    assert len(bob_feeds) == 2


@pytest.mark.asyncio
async def test_get_sequence_bounds_empty(repo: SqlAlchemyDeliveryFeedRepository):
    """フィードが無いストリームでは (None, None) を返す。"""
    bounds = await repo.get_sequence_bounds(SequenceName("never_used_seq"))
    assert bounds == (None, None)


@pytest.mark.asyncio
async def test_get_sequence_bounds_after_saves(
    repo: SqlAlchemyDeliveryFeedRepository,
):
    """保存後は (最小保持 seq, head) を返す。"""
    seq_name = SequenceName("bounds_seq")
    payload = SystemEventPayload(type=FeedEventType.JOIN, username=Username("alice"))
    for _ in range(3):
        await repo.save(
            DraftDeliveryFeed(
                sequence_name=seq_name, event_type=FeedEventType.JOIN, payload=payload
            )
        )

    min_retained, head = await repo.get_sequence_bounds(seq_name)
    assert min_retained == 1
    assert head == 3


@pytest.mark.asyncio
async def test_get_after_respects_limit_and_pages(
    repo: SqlAlchemyDeliveryFeedRepository,
):
    """get_after は limit で件数を境界化し、cursor を進めてページングできる。"""
    seq_name = SequenceName("paging_seq")
    payload = SystemEventPayload(type=FeedEventType.JOIN, username=Username("alice"))
    for _ in range(5):
        await repo.save(
            DraftDeliveryFeed(
                sequence_name=seq_name, event_type=FeedEventType.JOIN, payload=payload
            )
        )

    # 1 ページ目: seq 1,2
    page1 = await repo.get_after(seq_name, SequenceId(0), limit=2)
    assert [f.sequence_id.value for f in page1] == [1, 2]

    # 2 ページ目: cursor を 2 に進めて seq 3,4
    page2 = await repo.get_after(seq_name, SequenceId(2), limit=2)
    assert [f.sequence_id.value for f in page2] == [3, 4]

    # 3 ページ目: seq 5 のみ（残り 1 件）
    page3 = await repo.get_after(seq_name, SequenceId(4), limit=2)
    assert [f.sequence_id.value for f in page3] == [5]

    # 末尾以降は空
    page4 = await repo.get_after(seq_name, SequenceId(5), limit=2)
    assert page4 == []


def _dm_payload(
    seeded_users: dict[str, UserId], sender: str, recipient: str, task_id: int
) -> DirectRequestPayload:
    """sender→recipient の DM ペイロードを組み立てる。"""
    now = datetime.now(timezone.utc)
    return DirectRequestPayload(
        id=EntityId(task_id),
        sender_id=seeded_users[sender],
        recipient_id=seeded_users[recipient],
        sender_userid=Userid(sender),
        recipient_userid=Userid(recipient),
        sender=Username(sender),
        recipient=Username(recipient),
        text=TaskText("hi"),
        status=TaskStatus.REQUESTED,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_per_user_inbox_sequences_are_independent(
    repo: SqlAlchemyDeliveryFeedRepository, seeded_users: dict[str, UserId]
):
    """per-user inbox は互いに独立して 1 から連番採番され、混在しない。

    他人(charlie↔bob)の DM が間に挟まっても、alice の inbox は自分宛のものだけが
    1,2,... と連番になる（=フロントの seq-gap 誤検知が起きない）。
    """
    alice_inbox = direct_request_sequence("alice")
    bob_inbox = direct_request_sequence("bob")

    async def save_dm(inbox: SequenceName, sender: str, recipient: str, tid: int):
        return await repo.save(
            DraftDeliveryFeed(
                sequence_name=inbox,
                event_type=FeedEventType.DIRECT_REQUEST,
                payload=_dm_payload(seeded_users, sender, recipient, tid),
            )
        )

    # alice の inbox 1 件目 → 他人(charlie↔bob)の DM が bob inbox を消費 → alice 2 件目
    a1 = await save_dm(alice_inbox, "bob", "alice", 1)
    await save_dm(bob_inbox, "charlie", "bob", 2)
    await save_dm(bob_inbox, "charlie", "bob", 3)
    a2 = await save_dm(alice_inbox, "bob", "alice", 4)

    # alice の inbox は他人の DM に影響されず 1,2 と連番になる。
    assert (a1.sequence_id.value, a2.sequence_id.value) == (1, 2)

    # get_after は自分の inbox 名で問い合わせれば自分宛のみを返す。
    alice_feeds = await repo.get_after(
        alice_inbox, SequenceId(0), userid=Userid("alice")
    )
    assert [f.sequence_id.value for f in alice_feeds] == [1, 2]
    assert all(f.sequence_name == alice_inbox for f in alice_feeds)
