"""SQLAlchemy を使用した UserSettings リポジトリの実装。"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user_settings import UserSettings
from app.domain.primitives.primitives import UserId
from app.domain.repositories.user_settings_repository import UserSettingsRepository

from .orm_models import UserSettingsORM


class SqlAlchemyUserSettingsRepository(UserSettingsRepository):
    """SQLAlchemy を用いた UserSettingsRepository の実装。"""

    def __init__(self, session: AsyncSession):
        """SQLAlchemy セッションを初期化します。"""
        self._session = session

    async def get(self, user_id: UserId) -> UserSettings | None:
        """指定されたユーザー ID に対応する通知設定を取得します。"""
        stmt = select(UserSettingsORM).where(UserSettingsORM.user_id == user_id.value)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()
        if orm is None:
            return None
        return self._to_entity(orm)

    async def upsert(self, settings: UserSettings) -> UserSettings:
        """ユーザー設定を保存または更新（Upsert）します。"""
        insert_stmt = pg_insert(UserSettingsORM).values(
            user_id=settings.user_id.value,
            global_chat=settings.global_chat,
            direct_request=settings.direct_request,
            direct_request_updated=settings.direct_request_updated,
        )
        stmt = insert_stmt.on_conflict_do_update(
            index_elements=["user_id"],
            set_={
                "global_chat": insert_stmt.excluded.global_chat,
                "direct_request": insert_stmt.excluded.direct_request,
                "direct_request_updated": insert_stmt.excluded.direct_request_updated,
                "updated_at": datetime.now(timezone.utc),
            },
        )
        await self._session.execute(stmt)
        await self._session.flush()
        return settings

    def _to_entity(self, orm: UserSettingsORM) -> UserSettings:
        """ORM モデルをドメインエンティティに変換します。"""
        return UserSettings(
            user_id=UserId(orm.user_id),
            global_chat=orm.global_chat,
            direct_request=orm.direct_request,
            direct_request_updated=orm.direct_request_updated,
        )
