"""SQLAlchemy を用いた DeliveryFeed リポジトリの実装。"""

from datetime import datetime

from sqlalchemy import and_, delete, func, or_, select, text, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.primitives.feed import FeedEventType
from app.domain.primitives.primitives import Username

from ...application.outbox.delivery_feed import (
    DeliveryFeed,
    DraftDeliveryFeed,
    FeedStatus,
    SequenceId,
    SequenceName,
)
from ...application.repositories.delivery_feed_repository import DeliveryFeedRepository
from ..serialization import dict_to_payload, payload_to_dict
from .orm_models import DeliveryFeedORM, DeliverySequenceORM

# リカバリ取得の 1 ページあたり上限。単一クエリの結果サイズを境界化する。
RECOVERY_PAGE_SIZE = 500


class SqlAlchemyDeliveryFeedRepository(DeliveryFeedRepository):
    """DeliveryFeedRepository の SQLAlchemy による実装。"""

    def __init__(self, session: AsyncSession) -> None:
        """リポジトリを初期化します。"""
        self._session = session

    async def save(self, feed: DraftDeliveryFeed) -> DeliveryFeed:
        """フィードを保存します。この際、厳密連番の採番も行われます。"""
        # カウンタテーブルを更新して新しい ID を採番（行ロック）
        stmt = (
            pg_insert(DeliverySequenceORM)
            .values(name=feed.sequence_name.value, last_id=1)
            .on_conflict_do_update(
                index_elements=["name"],
                set_={"last_id": DeliverySequenceORM.last_id + 1},
            )
            .returning(DeliverySequenceORM.last_id)
        )
        result = await self._session.execute(stmt)
        new_id = result.scalar_one()

        orm = DeliveryFeedORM(
            sequence_name=feed.sequence_name.value,
            sequence_id=new_id,
            event_type=feed.event_type.value,
            payload=payload_to_dict(feed.payload),
            status=feed.status.value,
            created_at=feed.created_at,
        )
        self._session.add(orm)
        await self._session.flush()
        await self._session.execute(text("NOTIFY new_delivery_feed"))
        return self._to_domain(orm)

    async def get_pending(self, limit: int = 100) -> list[DeliveryFeed]:
        """未配信（PENDING）のフィードを取得します。
        FOR UPDATE SKIP LOCKED を使用します。
        """
        stmt = (
            select(DeliveryFeedORM)
            .where(DeliveryFeedORM.status == FeedStatus.PENDING.value)
            .order_by(DeliveryFeedORM.sequence_name, DeliveryFeedORM.sequence_id)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def mark_processed(
        self, feed_keys: list[tuple[SequenceName, SequenceId]]
    ) -> None:
        """指定されたフィードのステータスを PROCESSED に更新します。"""
        if not feed_keys:
            return

        conditions = [
            and_(
                DeliveryFeedORM.sequence_name == name.value,
                DeliveryFeedORM.sequence_id == seq_id.value,
            )
            for name, seq_id in feed_keys
        ]

        stmt = (
            update(DeliveryFeedORM)
            .where(or_(*conditions))
            .values(status=FeedStatus.PROCESSED.value)
        )

        await self._session.execute(stmt)

    async def get_after(
        self,
        sequence_name: SequenceName,
        after_id: SequenceId,
        username: Username | None = None,
        limit: int = RECOVERY_PAGE_SIZE,
    ) -> list[DeliveryFeed]:
        """指定された ID 以降のフィードを ``limit`` 件まで取得します。リカバリ用途です。

        ``sequence_id`` 昇順で最大 ``limit`` 件返すため、単一クエリの結果サイズが
        境界化される。残りは呼び出し側が cursor を進めてページングする。
        """
        stmt = (
            select(DeliveryFeedORM)
            .where(
                DeliveryFeedORM.sequence_name == sequence_name.value,
                DeliveryFeedORM.sequence_id > after_id.value,
            )
            .order_by(DeliveryFeedORM.sequence_id)
            .limit(limit)
        )

        if username:
            # global_chat イベント、または送信元/宛先が該当ユーザーの
            # request 系イベントをフィルタリング
            stmt = stmt.where(
                or_(
                    DeliveryFeedORM.event_type == FeedEventType.GLOBAL_CHAT.value,
                    DeliveryFeedORM.payload["sender"].astext == username.value,
                    DeliveryFeedORM.payload["recipient"].astext == username.value,
                )
            )

        result = await self._session.execute(stmt)
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def get_sequence_bounds(
        self, sequence_name: SequenceName
    ) -> tuple[int | None, int | None]:
        """``(保持中の最小 sequence_id, 採番済みの最大 sequence_id)`` を返します。"""
        min_retained = (
            await self._session.execute(
                select(func.min(DeliveryFeedORM.sequence_id)).where(
                    DeliveryFeedORM.sequence_name == sequence_name.value
                )
            )
        ).scalar_one_or_none()
        head = (
            await self._session.execute(
                select(DeliverySequenceORM.last_id).where(
                    DeliverySequenceORM.name == sequence_name.value
                )
            )
        ).scalar_one_or_none()
        return (min_retained, head)

    async def delete_old_processed_feeds(self, hours: int = 24) -> int:
        """指定された時間以上経過した PROCESSED ステータスのフィードを削除します。"""
        from datetime import timedelta, timezone

        threshold = datetime.now(timezone.utc) - timedelta(hours=hours)
        stmt = delete(DeliveryFeedORM).where(
            DeliveryFeedORM.status == FeedStatus.PROCESSED.value,
            DeliveryFeedORM.created_at < threshold,
        )
        result = await self._session.execute(stmt)
        return result.rowcount  # type: ignore[attr-defined]

    def _to_domain(self, orm: DeliveryFeedORM) -> DeliveryFeed:
        event_type = FeedEventType(orm.event_type)
        payload = dict_to_payload(event_type, orm.payload)

        return DeliveryFeed(
            sequence_name=SequenceName(orm.sequence_name),
            sequence_id=SequenceId(orm.sequence_id),
            event_type=event_type,
            payload=payload,
            status=FeedStatus(orm.status),
            created_at=orm.created_at,
        )
