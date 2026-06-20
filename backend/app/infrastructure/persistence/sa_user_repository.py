"""SQLAlchemy を使用した User リポジトリの実装。"""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.primitives.primitives import (
    HashedPassword,
    UserId,
    Userid,
    Username,
)
from app.domain.repositories.user_repository import UserRepository

from .orm_models import (
    MessageORM,
    TaskORM,
    UserORM,
)


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

    async def get_by_userid(self, userid: Userid) -> User | None:
        """指定されたログインIDに対応するユーザーを取得します。"""
        stmt = select(UserORM).where(UserORM.userid == userid.value)
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
            existing.userid = user.userid.value
            existing.username = user.username.value
            existing.hashed_password = user.hashed_password.value
            await self._session.flush()
            return self._to_entity(existing)
        else:
            orm = UserORM(
                id=user.id.value,
                userid=user.userid.value,
                username=user.username.value,
                hashed_password=user.hashed_password.value,
            )
            self._session.add(orm)
            await self._session.flush()
            return self._to_entity(orm)

    async def get_all(self) -> list[User]:
        """登録されているすべてのユーザーを取得します。"""
        stmt = select(UserORM).order_by(UserORM.userid.asc())
        res = await self._session.execute(stmt)
        return [self._to_entity(orm) for orm in res.scalars().all()]

    async def delete(self, user_id: UserId) -> bool:
        """指定された ID に対応するユーザーを削除します。"""
        stmt = select(UserORM).where(UserORM.id == user_id.value)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()
        if orm is None:
            return False
        await self._session.delete(orm)
        await self._session.flush()
        return True

    def _to_entity(self, orm: UserORM) -> User:
        """ORM モデルをドメインエンティティに変換します。"""
        return User(
            id=UserId(orm.id),
            userid=Userid(orm.userid),
            username=Username(orm.username),
            hashed_password=HashedPassword(orm.hashed_password),
        )

    async def update_username(
        self, user_id: UserId, old_username: Username, new_username: Username
    ) -> None:
        """ユーザーの表示名（username）を変更し、関連テーブルを一括更新します。"""
        # 1. messages テーブルの更新
        stmt_messages = (
            update(MessageORM)
            .where(MessageORM.user_id == user_id.value)
            .values(username=new_username.value)
        )
        await self._session.execute(stmt_messages)

        # 2. tasks テーブルの更新
        stmt_tasks_sender = (
            update(TaskORM)
            .where(TaskORM.sender_id == user_id.value)
            .values(sender=new_username.value)
        )
        stmt_tasks_recipient = (
            update(TaskORM)
            .where(TaskORM.recipient_id == user_id.value)
            .values(recipient=new_username.value)
        )
        await self._session.execute(stmt_tasks_sender)
        await self._session.execute(stmt_tasks_recipient)
        await self._session.flush()
