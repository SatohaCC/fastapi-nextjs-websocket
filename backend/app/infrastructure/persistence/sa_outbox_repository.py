"""SQLAlchemy を用いた DeliveryFeed リポジトリの実装。"""

from sqlalchemy import or_, select, update, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.delivery_feed import DeliveryFeed
from ...domain.repositories.delivery_feed_repository import DeliveryFeedRepository
from .orm_models import DeliveryFeedORM, DeliverySequenceORM


class SqlAlchemyDeliveryFeedRepository(DeliveryFeedRepository):
    """DeliveryFeedRepository の SQLAlchemy による実装。"""

    def __init__(self, session: AsyncSession) -> None:
        """リポジトリを初期化します。"""
        self._session = session

    async def save(self, feed: DeliveryFeed) -> DeliveryFeed:
        """フィードを保存します。この際、厳密連番の採番も行われます。"""
        if not feed.sequence_name:
            raise ValueError("sequence_name is required")

        # カウンタテーブルを更新して新しい ID を採番（行ロック）
        stmt = (
            update(DeliverySequenceORM)
            .where(DeliverySequenceORM.name == feed.sequence_name)
            .values(last_id=DeliverySequenceORM.last_id + 1)
            .returning(DeliverySequenceORM.last_id)
        )
        result = await self._session.execute(stmt)
        new_id = result.scalar_one_or_none()

        if new_id is None:
            # lifespan で事前に INSERT されているはずのシーケンスが存在しない。
            # フォールバックで INSERT すると並行リクエスト時に PK 制約違反が発生するため、
            # ここでは例外を発生させる。
            raise ValueError(
                f"Delivery sequence '{feed.sequence_name}' not found. "
                "Ensure it is seeded on application startup."
            )

        orm = DeliveryFeedORM(
            sequence_name=feed.sequence_name,
            sequence_id=new_id,
            event_type=feed.event_type,
            payload=feed.payload,
            status=feed.status,
            created_at=feed.created_at,
        )
        from sqlalchemy import text
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
            .where(DeliveryFeedORM.status == "PENDING")
            .order_by(DeliveryFeedORM.sequence_name, DeliveryFeedORM.sequence_id)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def mark_published(self, feed_keys: list[tuple[str, int]]) -> None:
        """指定されたフィードのステータスを PUBLISHED に更新します。"""
        if not feed_keys:
            return
        stmt = (
            update(DeliveryFeedORM)
            .where(
                tuple_(DeliveryFeedORM.sequence_name, DeliveryFeedORM.sequence_id).in_(
                    feed_keys
                )
            )
            .values(status="PUBLISHED")
        )
        await self._session.execute(stmt)

    async def get_after(
        self, sequence_name: str, after_id: int, username: str | None = None
    ) -> list[DeliveryFeed]:
        """指定された ID 以降のフィードを取得します。リカバリ用途です。"""
        stmt = (
            select(DeliveryFeedORM)
            .where(
                DeliveryFeedORM.sequence_name == sequence_name,
                DeliveryFeedORM.sequence_id > after_id,
            )
            .order_by(DeliveryFeedORM.sequence_id)
        )

        if username:
            # message イベント、または送信元/宛先が該当ユーザーの
            # request 系イベントをフィルタリング
            stmt = stmt.where(
                or_(
                    DeliveryFeedORM.event_type == "message",
                    DeliveryFeedORM.payload["sender"].astext == username,
                    DeliveryFeedORM.payload["recipient"].astext == username,
                )
            )

        result = await self._session.execute(stmt)
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def delete_old_published_feeds(self, hours: int = 24) -> int:
        """指定された時間以上経過した PUBLISHED ステータスのフィードを削除します。"""
        from datetime import datetime, timedelta, timezone
        from sqlalchemy import delete
        threshold = datetime.now(timezone.utc) - timedelta(hours=hours)
        stmt = (
            delete(DeliveryFeedORM)
            .where(
                DeliveryFeedORM.status == "PUBLISHED",
                DeliveryFeedORM.created_at < threshold,
            )
        )
        result = await self._session.execute(stmt)
        return result.rowcount

    def _to_domain(self, orm: DeliveryFeedORM) -> DeliveryFeed:
        return DeliveryFeed(
            sequence_name=orm.sequence_name,
            sequence_id=orm.sequence_id,
            event_type=orm.event_type,
            payload=orm.payload,
            status=orm.status,
            created_at=orm.created_at,
        )
