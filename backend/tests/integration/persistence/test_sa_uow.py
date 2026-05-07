"""SqlAlchemyUnitOfWork の統合テスト。"""

from datetime import datetime, timezone

import pytest

from app.domain.entities.delivery_feed import DraftDeliveryFeed
from app.domain.entities.message import DraftMessage
from app.domain.entities.payload import MessagePayload
from app.domain.primitives.feed import FeedEventType, SequenceId, SequenceName
from app.domain.primitives.primitives import EntityId, MessageText, Username
from app.infrastructure.persistence.sa_uow import SqlAlchemyUnitOfWork


@pytest.mark.asyncio
async def test_uow_commit_saves_multiple_entities(db_uow: SqlAlchemyUnitOfWork):
    """メッセージと Outbox 両方の保存が、1つのトランザクションで確定することを確認。"""
    async with db_uow:
        # 1. メッセージ保存
        msg = await db_uow.messages.save(
            DraftMessage(
                username=Username("alice"),
                text=MessageText("hello"),
                created_at=datetime.now(timezone.utc),
            )
        )

        # 2. Outbox 保存
        await db_uow.outbox.save(
            DraftDeliveryFeed(
                sequence_name=SequenceName("chat"),
                event_type=FeedEventType.MESSAGE,
                payload=MessagePayload(
                    id=msg.id,
                    username=msg.username,
                    text=msg.text,
                    created_at=msg.created_at,
                ),
            )
        )

        await db_uow.commit()

    # コミットされたことを確認
    # (同一 db_session 内なので flush 済み)
    # get_after で取得できるか確認
    msgs = await db_uow.messages.get_after(EntityId(0))
    feeds = await db_uow.outbox.get_after(SequenceName("chat"), SequenceId(0))

    assert len(msgs) == 1
    assert len(feeds) == 1


@pytest.mark.asyncio
async def test_uow_rollback_on_exception(db_uow: SqlAlchemyUnitOfWork):
    """例外発生時に、それまでの書き込みがすべてロールバックされることを確認。"""
    try:
        async with db_uow:
            await db_uow.messages.save(
                DraftMessage(
                    username=Username("alice"),
                    text=MessageText("fail"),
                    created_at=datetime.now(timezone.utc),
                )
            )
            # 意図的に例外を発生させる
            raise ValueError("Something went wrong")
    except ValueError:
        pass

    # ロールバックされているので、1件も存在しないはず
    msgs = await db_uow.messages.get_after(EntityId(0))
    assert len(msgs) == 0
