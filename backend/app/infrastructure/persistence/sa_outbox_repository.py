"""SQLAlchemy を用いた DeliveryFeed リポジトリの実装。"""

import hashlib
from datetime import datetime

from sqlalchemy import and_, delete, func, or_, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.primitives.feed import FeedEventType
from app.domain.primitives.primitives import Userid

from ...application.outbox.delivery_feed import (
    DeliveryFeed,
    DraftDeliveryFeed,
    FeedStatus,
    SequenceId,
    SequenceName,
)
from ...application.repositories.delivery_feed_repository import DeliveryFeedRepository
from ..serialization import dict_to_payload, payload_to_dict
from .orm_models import DeliveryFeedORM

# リカバリ取得の 1 ページあたり上限。単一クエリの結果サイズを境界化する。
RECOVERY_PAGE_SIZE = 500


def _sequence_ident(name: str) -> str:
    """``sequence_name`` から、ネイティブ SEQUENCE オブジェクト名を導出します。

    ``sequence_name`` は ``direct_request:{userid}`` のようにユーザーごとに
    動的生成され、PostgreSQL の識別子長制限（NAMEDATALEN、63バイト）を超える
    可能性があるため、名前をそのまま識別子として使わず、SHA-256 の先頭32桁hex
    による固定長（36文字）の決定的な識別子に変換する。ハッシュ出力は
    ``[0-9a-f]`` のみなので、引用符なしで安全に SQL 文へ埋め込める。
    """
    digest = hashlib.sha256(name.encode()).hexdigest()[:32]
    return f"seq_{digest}"


class SqlAlchemyDeliveryFeedRepository(DeliveryFeedRepository):
    """DeliveryFeedRepository の SQLAlchemy による実装。"""

    def __init__(self, session: AsyncSession) -> None:
        """リポジトリを初期化します。"""
        self._session = session

    async def save(self, feed: DraftDeliveryFeed) -> DeliveryFeed:
        """フィードを保存します。この際、厳密連番の採番も行われます。

        採番は PostgreSQL ネイティブの SEQUENCE オブジェクト（``nextval()``）を用いる。
        ``nextval()`` は呼び出し元トランザクションがロールバックしても値が戻らない
        （非トランザクショナル）特性を持つため、行ロックによる直列化を発生させない。
        """
        ident = _sequence_ident(feed.sequence_name.value)
        # CREATE SEQUENCE IF NOT EXISTS は冪等な軽量 catalog 操作であり、
        # 行ロックのような競合は発生しないため、毎回呼んでも問題ない。
        await self._session.execute(text(f"CREATE SEQUENCE IF NOT EXISTS {ident}"))
        result = await self._session.execute(text(f"SELECT nextval('{ident}')"))
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
        userid: Userid | None = None,
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

        if userid:
            # global_chat イベント、または送信元/宛先が該当ユーザーの
            # request 系イベントをフィルタリング
            stmt = stmt.where(
                or_(
                    DeliveryFeedORM.event_type == FeedEventType.GLOBAL_CHAT.value,
                    DeliveryFeedORM.payload["sender_userid"].astext == userid.value,
                    DeliveryFeedORM.payload["recipient_userid"].astext == userid.value,
                    and_(
                        DeliveryFeedORM.payload["sender_userid"].astext.is_(None),
                        or_(
                            DeliveryFeedORM.payload["sender"].astext == userid.value,
                            DeliveryFeedORM.payload["recipient"].astext == userid.value,
                        ),
                    ),
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

        ident = _sequence_ident(sequence_name.value)
        exists = (
            await self._session.execute(
                text("SELECT to_regclass(:ident) IS NOT NULL").bindparams(ident=ident)
            )
        ).scalar_one()
        head: int | None = None
        if exists:
            last_value, is_called = (
                await self._session.execute(
                    text(f"SELECT last_value, is_called FROM {ident}")
                )
            ).one()
            # is_called が false の場合、nextval() が一度も呼ばれていない
            # （= まだ採番されたフィードが無い）ことを意味する。
            head = int(last_value) if is_called else None

        return (min_retained, head)

    async def drop_sequence(self, sequence_name: SequenceName) -> None:
        """指定シーケンス名に対応するネイティブ SEQUENCE を削除します。

        ユーザー退会時など、per-user inbox（``direct_request:{userid}``）の
        後始末として呼び出される。``DROP SEQUENCE`` 自体は通常の DDL として
        トランザクショナルに振る舞う（呼び出し元トランザクションのロールバックで
        削除も取り消される）。
        """
        ident = _sequence_ident(sequence_name.value)
        await self._session.execute(text(f"DROP SEQUENCE IF EXISTS {ident}"))

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
