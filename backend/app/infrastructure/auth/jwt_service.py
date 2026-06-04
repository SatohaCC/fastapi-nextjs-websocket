"""PyJWT を使用した JWT 認証サービスの実装。"""

from datetime import datetime, timedelta, timezone

import jwt

from app.domain.primitives.primitives import AuthToken, Password, RefreshToken, Username

from ..config import settings

_ACCESS_TYPE = "access"
_REFRESH_TYPE = "refresh"


class JwtServiceImpl:
    """JwtService の実装。"""

    def authenticate(self, username: Username, password: Password) -> bool:
        """ユーザー名とパスワードの照合を行います。"""
        return settings.USERS.get(username) == password

    def create_token(self, username: Username) -> tuple[AuthToken, RefreshToken]:
        """アクセストークンとリフレッシュトークンのペアを生成して返します。"""
        now = datetime.now(timezone.utc)

        access_payload = {
            "sub": username.value,
            "type": _ACCESS_TYPE,
            "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        access_token = AuthToken(
            jwt.encode(
                access_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
            )
        )

        refresh_payload = {
            "sub": username.value,
            "type": _REFRESH_TYPE,
            "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        }
        refresh_token = RefreshToken(
            jwt.encode(
                refresh_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
            )
        )

        return access_token, refresh_token

    def verify_token(self, token: AuthToken) -> Username | None:
        """アクセストークンを検証し、ユーザー名を返します。リフレッシュトークンは拒否します。"""
        try:
            payload = jwt.decode(
                token.value, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            if payload.get("type") != _ACCESS_TYPE:
                return None
            username_str: str | None = payload.get("sub")
            if username_str is None:
                return None
            return Username(username_str)
        except jwt.PyJWTError:
            return None

    def verify_refresh_token(self, token: RefreshToken) -> Username | None:
        """リフレッシュトークンを検証し、ユーザー名を返します。アクセストークンは拒否します。"""
        try:
            payload = jwt.decode(
                token.value, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            if payload.get("type") != _REFRESH_TYPE:
                return None
            username_str: str | None = payload.get("sub")
            if username_str is None:
                return None
            return Username(username_str)
        except jwt.PyJWTError:
            return None
