"""SQLAlchemy を用いた DeliveryFeed リポジトリの実装。"""

from sqlalchemy import and_, delete, or_, select, text, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.primitives.feed import (
    FeedEventType,
    FeedStatus,
    SequenceId,
    SequenceName,
)
from app.domain.primitives.primitives import Username

from ...domain.entities.delivery_feed import DeliveryFeed, DraftDeliveryFeed
from ...domain.entities.payload import (
    FeedPayload,
    MessagePayload,
    RequestPayload,
    RequestUpdatePayload,
    SystemEventPayload,
)
from ...domain.repositories.delivery_feed_repository import DeliveryFeedRepository
from .orm_models import DeliveryFeedORM, DeliverySequenceORM


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
            payload=feed.payload.to_dict(),
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

        # tuple のリストから複合条件を作成
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
    ) -> list[DeliveryFeed]:
        """指定された ID 以降のフィードを取得します。リカバリ用途です。"""
        stmt = (
            select(DeliveryFeedORM)
            .where(
                DeliveryFeedORM.sequence_name == sequence_name.value,
                DeliveryFeedORM.sequence_id > after_id.value,
            )
            .order_by(DeliveryFeedORM.sequence_id)
        )

        if username:
            # message イベント、または送信元/宛先が該当ユーザーの
            # request 系イベントをフィルタリング
            stmt = stmt.where(
                or_(
                    DeliveryFeedORM.event_type == FeedEventType.MESSAGE.value,
                    DeliveryFeedORM.payload["sender"].astext == username.value,
                    DeliveryFeedORM.payload["recipient"].astext == username.value,
                )
            )

        result = await self._session.execute(stmt)
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def delete_old_processed_feeds(self, hours: int = 24) -> int:
        """指定された時間以上経過した PROCESSED ステータスのフィードを削除します。"""
        from datetime import datetime, timedelta, timezone

        threshold = datetime.now(timezone.utc) - timedelta(hours=hours)
        stmt = delete(DeliveryFeedORM).where(
            DeliveryFeedORM.status == FeedStatus.PROCESSED.value,
            DeliveryFeedORM.created_at < threshold,
        )
        result = await self._session.execute(stmt)
        return result.rowcount

    def _to_domain(self, orm: DeliveryFeedORM) -> DeliveryFeed:
        event_type = FeedEventType(orm.event_type)
        payload_dict = orm.payload

        # デシリアライズ
        payload: FeedPayload
        if event_type == FeedEventType.MESSAGE:
            payload = MessagePayload(
                id=payload_dict["id"],
                username=payload_dict["username"],
                text=payload_dict["text"],
                created_at=payload_dict["created_at"],
            )
        elif event_type == FeedEventType.REQUEST:
            payload = RequestPayload(
                id=payload_dict["id"],
                sender=payload_dict["sender"],
                recipient=payload_dict["recipient"],
                text=payload_dict["text"],
                status=payload_dict["status"],
                created_at=payload_dict["created_at"],
                updated_at=payload_dict["updated_at"],
            )
        elif event_type == FeedEventType.REQUEST_UPDATED:
            payload = RequestUpdatePayload(
                id=payload_dict["id"],
                status=payload_dict["status"],
                sender=payload_dict["sender"],
                recipient=payload_dict["recipient"],
                updated_at=payload_dict["updated_at"],
            )
        else:
            payload = SystemEventPayload(
                type=payload_dict["type"],
                username=payload_dict["username"],
            )

        return DeliveryFeed(
            sequence_name=SequenceName(orm.sequence_name),
            sequence_id=SequenceId(orm.sequence_id),
            event_type=event_type,
            payload=payload,
            status=FeedStatus(orm.status),
            created_at=orm.created_at,
        )
