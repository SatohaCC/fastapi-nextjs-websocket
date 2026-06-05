"""ユーザー認証とトークン発行を管理するアプリケーションサービス。"""

from app.domain.primitives.primitives import AuthToken, Password, RefreshToken, Username

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

    async def login(
        self, username: Username, password: Password
    ) -> tuple[AuthToken, RefreshToken] | None:
        """ユーザー認証を行い、成功した場合はトークンペアを返します。"""
        async with self._uow as uow:
            user = await uow.users.get_by_username(username)
            if user is None:
                return None

            if self._password_verifier.verify(password.value, user.hashed_password):
                return self._jwt.create_token(username)
        return None

    def refresh(
        self, refresh_token: RefreshToken
    ) -> tuple[AuthToken, RefreshToken] | None:
        """リフレッシュトークンを検証し、新しいトークンペアを返します。"""
        username = self._jwt.verify_refresh_token(refresh_token)
        if username is None:
            return None
        return self._jwt.create_token(username)

    def get_user_from_token(self, token: AuthToken) -> Username | None:
        """アクセストークンを検証し、ユーザー名を取得します。"""
        return self._jwt.verify_token(token)

    async def get_all_usernames(self) -> list[Username]:
        """全ユーザー名を取得します。"""
        async with self._uow as uow:
            users = await uow.users.get_all()
            return [u.username for u in users]
