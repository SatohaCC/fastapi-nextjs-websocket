"""SQLAlchemy を使用した User リポジトリの実装。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.primitives.primitives import UserId, Username
from app.domain.repositories.user_repository import UserRepository

from .orm_models import UserORM


class SqlAlchemyUserRepository(UserRepository):
    """SQLAlchemy を用いた UserRepository の実装。"""

    def __init__(self, session: AsyncSession):
        """SQLAlchemy セッションを初期化します。"""
        self._session = session

    async def get_by_id(self, user_id: UserId) -> User | None:
        """指定された ID に対応するユーザーを取得します。"""
        stmt = select(UserORM).where(UserORM.id == user_id.value)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()
        if orm is None:
            return None
        return self._to_entity(orm)

    async def get_by_username(self, username: Username) -> User | None:
        """指定されたユーザー名に対応するユーザーを取得します。"""
        stmt = select(UserORM).where(UserORM.username == username.value)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()
        if orm is None:
            return None
        return self._to_entity(orm)

    async def save(self, user: User) -> User:
        """ユーザー情報を保存または更新（新規作成または更新）します。"""
        stmt = select(UserORM).where(UserORM.id == user.id.value)
        res = await self._session.execute(stmt)
        existing = res.scalar_one_or_none()
        if existing:
            existing.username = user.username.value
            existing.hashed_password = user.hashed_password
            await self._session.flush()
            return self._to_entity(existing)
        else:
            orm = UserORM(
                id=user.id.value,
                username=user.username.value,
                hashed_password=user.hashed_password,
            )
            self._session.add(orm)
            await self._session.flush()
            return self._to_entity(orm)

    async def get_all(self) -> list[User]:
        """登録されているすべてのユーザーを取得します。"""
        stmt = select(UserORM).order_by(UserORM.username.asc())
        res = await self._session.execute(stmt)
        return [self._to_entity(orm) for orm in res.scalars().all()]

    def _to_entity(self, orm: UserORM) -> User:
        """ORM モデルをドメインエンティティに変換します。"""
        return User(
            id=UserId(orm.id),
            username=Username(orm.username),
            hashed_password=orm.hashed_password,
        )
