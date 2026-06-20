"""SQLAlchemy を使用した RefreshToken リポジトリの実装。"""

from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.refresh_token import RefreshToken
from app.domain.primitives.primitives import (
    IpAddress,
    SessionId,
    TokenHash,
    UserAgent,
    UserId,
)
from app.domain.repositories.refresh_token_repository import RefreshTokenRepository

from .orm_models import RefreshTokenORM


class SqlAlchemyRefreshTokenRepository(RefreshTokenRepository):
    """SQLAlchemy を用いた RefreshTokenRepository の実装。"""

    def __init__(self, session: AsyncSession):
        """SQLAlchemy セッションを初期化します。"""
        self._session = session

    async def get_by_id(self, token_id: SessionId) -> RefreshToken | None:
        """指定されたIDに対応するリフレッシュトークンを取得します。"""
        stmt = select(RefreshTokenORM).where(RefreshTokenORM.id == token_id.value)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()
        if orm is None:
            return None
        return self._to_entity(orm)

    async def get_by_hash(self, token_hash: TokenHash) -> RefreshToken | None:
        """ハッシュ値に対応するリフレッシュトークンを取得します。"""
        stmt = select(RefreshTokenORM).where(
            RefreshTokenORM.token_hash == token_hash.value
        )
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()
        if orm is None:
            return None
        return self._to_entity(orm)

    async def get_by_user_id(self, user_id: UserId) -> list[RefreshToken]:
        """指定されたユーザーに紐づくすべてのリフレッシュトークンを取得します。"""
        stmt = (
            select(RefreshTokenORM)
            .where(RefreshTokenORM.user_id == user_id.value)
            .order_by(RefreshTokenORM.created_at.desc())
        )
        res = await self._session.execute(stmt)
        orms = res.scalars().all()
        return [self._to_entity(orm) for orm in orms]

    async def save(self, refresh_token: RefreshToken) -> RefreshToken:
        """リフレッシュトークンを保存または更新します。"""
        stmt = select(RefreshTokenORM).where(
            RefreshTokenORM.id == refresh_token.id.value
        )
        res = await self._session.execute(stmt)
        existing = res.scalar_one_or_none()
        if existing:
            existing.user_id = refresh_token.user_id.value
            existing.token_hash = refresh_token.token_hash.value
            existing.expires_at = refresh_token.expires_at
            existing.ip_address = (
                refresh_token.ip_address.value if refresh_token.ip_address else None
            )
            existing.user_agent = (
                refresh_token.user_agent.value if refresh_token.user_agent else None
            )
            await self._session.flush()
            return self._to_entity(existing)
        else:
            orm = RefreshTokenORM(
                id=refresh_token.id.value,
                user_id=refresh_token.user_id.value,
                token_hash=refresh_token.token_hash.value,
                expires_at=refresh_token.expires_at,
                created_at=refresh_token.created_at,
                ip_address=refresh_token.ip_address.value
                if refresh_token.ip_address
                else None,
                user_agent=refresh_token.user_agent.value
                if refresh_token.user_agent
                else None,
            )
            self._session.add(orm)
            await self._session.flush()
            return self._to_entity(orm)

    async def delete_by_id(self, token_id: SessionId) -> bool:
        """指定されたIDに対応するリフレッシュトークンを物理削除します。"""
        stmt = delete(RefreshTokenORM).where(RefreshTokenORM.id == token_id.value)
        res = await self._session.execute(stmt)
        return bool(res.rowcount)  # type: ignore[attr-defined]

    async def delete_by_hash(self, token_hash: TokenHash) -> bool:
        """ハッシュ値に対応するリフレッシュトークンを物理削除します。"""
        stmt = delete(RefreshTokenORM).where(
            RefreshTokenORM.token_hash == token_hash.value
        )
        res = await self._session.execute(stmt)
        return bool(res.rowcount)  # type: ignore[attr-defined]

    async def delete_by_user_id(self, user_id: UserId) -> None:
        """指定されたユーザーに紐づくすべてのリフレッシュトークンを物理削除します。"""
        stmt = delete(RefreshTokenORM).where(RefreshTokenORM.user_id == user_id.value)
        await self._session.execute(stmt)

    async def delete_expired(self, now: datetime) -> int:
        """指定された基準日時より有効期限の古いリフレッシュトークンをすべて物理削除し、削除件数を返します。"""
        stmt = delete(RefreshTokenORM).where(RefreshTokenORM.expires_at < now)
        res = await self._session.execute(stmt)
        return res.rowcount  # type: ignore[attr-defined]

    def _to_entity(self, orm: RefreshTokenORM) -> RefreshToken:
        """ORM モデルをドメインエンティティに変換します。"""
        return RefreshToken(
            id=SessionId(orm.id),
            user_id=UserId(orm.user_id),
            token_hash=TokenHash(orm.token_hash),
            expires_at=orm.expires_at,
            created_at=orm.created_at,
            ip_address=IpAddress(orm.ip_address) if orm.ip_address else None,
            user_agent=UserAgent(orm.user_agent) if orm.user_agent else None,
        )
