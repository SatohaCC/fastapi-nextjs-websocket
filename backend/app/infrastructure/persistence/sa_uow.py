"""SQLAlchemy を使用した Unit of Work の実装。"""

from sqlalchemy.ext.asyncio import AsyncSession

from ...application.uow import UnitOfWork
from ...domain.repositories.delivery_feed_repository import DeliveryFeedRepository
from ...domain.repositories.message_repository import MessageRepository
from ...domain.repositories.request_repository import RequestRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    """SQLAlchemy を使用した UnitOfWork の実装。"""

    def __init__(
        self,
        session: AsyncSession,
        requests: RequestRepository,
        messages: MessageRepository,
        outbox: DeliveryFeedRepository,
    ):
        """UnitOfWork を初期化します。"""
        self._session = session
        self.requests = requests
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
