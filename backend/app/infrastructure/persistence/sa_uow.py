"""SQLAlchemy を使用した Unit of Work の実装。"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...application.outbox.repository import DeliveryFeedRepository
from ...application.uow import UnitOfWork
from ...domain.repositories.message_repository import MessageRepository
from ...domain.repositories.task_repository import TaskRepository
from .sa_message_repository import SqlAlchemyMessageRepository
from .sa_outbox_repository import SqlAlchemyDeliveryFeedRepository
from .sa_task_repository import SqlAlchemyTaskRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    """SQLAlchemy を使用した UnitOfWork の実装。"""

    def __init__(
        self,
        session: AsyncSession,
        tasks: TaskRepository,
        messages: MessageRepository,
        outbox: DeliveryFeedRepository,
    ):
        """UnitOfWork を初期化します。"""
        self._session = session
        self.tasks = tasks
        self.messages = messages
        self.outbox = outbox

    async def commit(self) -> None:
        """セッションの変更を確定させます。"""
        await self._session.commit()

    async def rollback(self) -> None:
        """セッションの変更をロールバックします。"""
        await self._session.rollback()

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        """コンテキストマネージャーの開始。"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """コンテキストマネージャーの終了。"""
        # 例外の有無に関わらず、未コミットの変更があればロールバックする。
        # (commit() が呼ばれた後であれば SQLAlchemy 側で適切に処理される)
        await self.rollback()


@asynccontextmanager
async def make_standalone_uow(
    session_factory: async_sessionmaker,
) -> AsyncGenerator["SqlAlchemyUnitOfWork", None]:
    """セッションのライフサイクルを内部管理するスタンドアロン UoW を生成するファクトリ。

    バックグラウンドワーカーなど、FastAPI の DI 外でイテレーションごとに
    新しいセッションを作成したい場合に使用します。
    """
    async with session_factory() as session:
        yield SqlAlchemyUnitOfWork(
            session,
            SqlAlchemyTaskRepository(session),
            SqlAlchemyMessageRepository(session),
            SqlAlchemyDeliveryFeedRepository(session),
        )
