"""SQLAlchemy を使用したリクエストリポジトリの実装。"""

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.direct_request import DirectRequest, DraftDirectRequest
from ...domain.primitives.primitives import EntityId, RequestText, Username
from ...domain.primitives.request_status import RequestStatus
from ...domain.repositories.request_repository import RequestRepository
from .orm_models import RequestORM


class SqlAlchemyRequestRepository(RequestRepository):
    """SQLAlchemy を使用した RequestRepository の実装。"""

    def __init__(self, session: AsyncSession):
        """SQLAlchemy セッションを初期化します。"""
        self._session = session

    async def save(self, request: DraftDirectRequest) -> DirectRequest:
        """エンティティを DB に保存（新規作成または更新）します。"""
        orm = RequestORM(
            sender=request.sender.value,
            recipient=request.recipient.value,
            text=request.text.value,
            status=request.status.value,
            created_at=request.created_at,
            updated_at=request.updated_at
            if isinstance(request, DirectRequest)
            else request.created_at,
        )
        if isinstance(request, DirectRequest):
            orm.id = request.id.value
            orm = await self._session.merge(orm)
        else:
            self._session.add(orm)

        # Note: commit() は UoW が担当するため、ここでは行わない
        await self._session.flush()
        await self._session.refresh(orm)
        return self._to_entity(orm)

    async def get_by_id(self, request_id: EntityId) -> DirectRequest | None:
        """ID でリクエストを検索します。"""
        res = await self._session.execute(
            select(RequestORM).where(RequestORM.id == request_id.value)
        )
        orm = res.scalar_one_or_none()
        return self._to_entity(orm) if orm else None

    async def get_for_user(self, username: Username) -> list[DirectRequest]:
        """ユーザーに関連するリクエストを全件取得します（送信、受信の両方）。"""
        stmt = (
            select(RequestORM)
            .where(
                or_(
                    RequestORM.sender == username.value,
                    RequestORM.recipient == username.value,
                )
            )
            .order_by(RequestORM.created_at.asc())
        )
        res = await self._session.execute(stmt)
        return [self._to_entity(row) for row in res.scalars().all()]

    async def get_after(
        self, username: Username, after_id: EntityId
    ) -> list[DirectRequest]:
        """指定したID以降のユーザー関連リクエストを取得します。"""
        stmt = (
            select(RequestORM)
            .where(
                or_(
                    RequestORM.sender == username.value,
                    RequestORM.recipient == username.value,
                ),
                RequestORM.id > after_id.value,
            )
            .order_by(RequestORM.id.asc())
        )
        res = await self._session.execute(stmt)
        return [self._to_entity(row) for row in res.scalars().all()]

    def _to_entity(self, orm: RequestORM) -> DirectRequest:
        """ORM モデルをドメインエンティティに変換します。"""
        return DirectRequest(
            id=EntityId(orm.id),
            sender=Username(orm.sender),
            recipient=Username(orm.recipient),
            text=RequestText(orm.text),
            status=RequestStatus(orm.status),
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )
