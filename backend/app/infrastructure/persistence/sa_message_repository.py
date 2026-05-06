"""SQLAlchemy を使用したメッセージリポジトリの実装。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.message import Message
from ...domain.primitives.primitives import EntityId, MessageText, Username
from ...domain.repositories.message_repository import MessageRepository
from .orm_models import MessageORM


class SqlAlchemyMessageRepository(MessageRepository):
    """SQLAlchemy を使用した MessageRepository の実装クラス。
    PostgreSQL データベースへの非同期アクセスを担当します。
    """

    def __init__(self, session: AsyncSession) -> None:
        """SQLAlchemy セッションを初期化します。"""
        self._session = session

    async def save(self, message: Message) -> Message:
        """メッセージエンティティをデータベースに保存します。"""
        orm_msg = MessageORM(
            username=message.username.value,
            text=message.text.value,
            created_at=message.created_at,
        )
        self._session.add(orm_msg)
        # Note: commit() は UoW が担当するため、ここでは行わない
        await self._session.flush()
        await self._session.refresh(orm_msg)
        return self._to_domain(orm_msg)

    async def get_after(self, after_id: EntityId) -> list[Message]:
        """指定された ID 以降のメッセージを古い順（昇順）に取得します。"""
        result = await self._session.execute(
            select(MessageORM)
            .where(MessageORM.id > after_id.value)
            .order_by(MessageORM.id.asc())
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def get_recent(self, limit: int = 50) -> list[Message]:
        """最新のメッセージを指定件数分、古い順（昇順）に並べ替えて取得します。"""
        result = await self._session.execute(
            select(MessageORM).order_by(MessageORM.created_at.desc()).limit(limit)
        )
        # DBからは新しい順で取れるため、表示用に反転させる
        msgs = [self._to_domain(m) for m in result.scalars().all()]
        msgs.reverse()
        return msgs

    @staticmethod
    def _to_domain(orm_msg: MessageORM) -> Message:
        """ORM モデルをドメインエンティティに変換します。"""
        return Message(
            id=EntityId(orm_msg.id),
            username=Username(orm_msg.username),
            text=MessageText(orm_msg.text),
            created_at=orm_msg.created_at,
        )
