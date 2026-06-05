"""ユーザー認証とトークン発行を管理するアプリケーションサービス。"""

import hashlib
from datetime import datetime, timedelta, timezone

from app.domain.entities.refresh_token import RefreshToken as RefreshTokenEntity
from app.domain.entities.user import User
from app.domain.primitives.primitives import (
    AuthToken,
    Password,
    RefreshToken,
    UserId,
    Username,
)
from app.infrastructure.auth.uuid7 import generate_uuid7
from app.infrastructure.config import settings

from ..interfaces.auth import TokenProvider
from ..interfaces.password import PasswordVerifier
from ..uow import UnitOfWork


class AuthService:
    """ユーザー認証とトークン発行を管理するアプリケーションサービス。"""

    def __init__(
        self, uow: UnitOfWork, jwt: TokenProvider, password_verifier: PasswordVerifier
    ) -> None:
        """認証サービスを初期化します。"""
        self._uow = uow
        self._jwt = jwt
        self._password_verifier = password_verifier

    def _hash_token(self, token: str) -> str:
        """トークン文字列を SHA-256 でハッシュ化して 16 進数文字列を返します。"""
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    async def login(
        self,
        username: Username,
        password: Password,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[AuthToken, RefreshToken] | None:
        """ユーザー認証を行い、成功した場合はトークンペアを返します。"""
        async with self._uow as uow:
            user = await uow.users.get_by_username(username)
            if user is None:
                return None

            if self._password_verifier.verify(password.value, user.hashed_password):
                access_token, refresh_token = self._jwt.create_token(user.id)

                # リフレッシュトークンをDBに保存
                hash_val = self._hash_token(refresh_token.value)
                now = datetime.now(timezone.utc)
                expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

                db_token = RefreshTokenEntity(
                    id=generate_uuid7(),
                    user_id=user.id,
                    token_hash=hash_val,
                    expires_at=expires_at,
                    created_at=now,
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
                await uow.refresh_tokens.save(db_token)
                await uow.commit()

                return access_token, refresh_token
        return None

    async def refresh(
        self,
        refresh_token: RefreshToken,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[AuthToken, RefreshToken] | None:
        """リフレッシュトークンを検証し、新しいトークンペアを返します。"""
        # JWTとしての形式・有効期限を検証
        user_id = self._jwt.verify_refresh_token(refresh_token)
        if user_id is None:
            return None

        hash_val = self._hash_token(refresh_token.value)

        async with self._uow as uow:
            # DBにハッシュ値のレコードが存在するか確認
            db_token = await uow.refresh_tokens.get_by_hash(hash_val)
            if db_token is None:
                return None

            # DB上の有効期限チェック（安全のため）
            now = datetime.now(timezone.utc)
            if db_token.expires_at < now:
                await uow.refresh_tokens.delete_by_hash(hash_val)
                await uow.commit()
                return None

            # 古いリフレッシュトークンを物理削除
            await uow.refresh_tokens.delete_by_hash(hash_val)

            # 新しいトークンペアを発行（db_token.user_id を使用）
            new_access_token, new_refresh_token = self._jwt.create_token(
                db_token.user_id
            )

            # 新しいリフレッシュトークンをDBに保存
            new_hash_val = self._hash_token(new_refresh_token.value)
            new_expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

            new_db_token = RefreshTokenEntity(
                id=generate_uuid7(),
                user_id=db_token.user_id,
                token_hash=new_hash_val,
                expires_at=new_expires_at,
                created_at=now,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            await uow.refresh_tokens.save(new_db_token)
            await uow.commit()

            return new_access_token, new_refresh_token

    async def logout(self, refresh_token: RefreshToken) -> bool:
        """指定されたリフレッシュトークンをDBから物理削除します。"""
        hash_val = self._hash_token(refresh_token.value)
        async with self._uow as uow:
            success = await uow.refresh_tokens.delete_by_hash(hash_val)
            await uow.commit()
            return success

    def get_user_id_from_token(self, token: AuthToken) -> UserId | None:
        """アクセストークンを検証し、ユーザー ID を取得します。"""
        return self._jwt.verify_token(token)

    async def get_user_by_id(self, user_id: UserId) -> User | None:
        """ユーザー ID でユーザーを取得します。"""
        async with self._uow as uow:
            return await uow.users.get_by_id(user_id)

    async def get_all_usernames(self) -> list[Username]:
        """全ユーザー名を取得します。"""
        async with self._uow as uow:
            users = await uow.users.get_all()
            return [u.username for u in users]
