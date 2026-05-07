"""PyJWT を使用した JWT 認証サービスの実装。"""

from datetime import datetime, timedelta, timezone

import jwt

from app.domain.primitives.primitives import AuthToken, Password, Username

from ..config import settings


class JwtServiceImpl:
    """JwtService の実装。PyJWT を使用します。"""

    def authenticate_user(self, username: Username, password: Password) -> bool:
        """ユーザー名とパスワードの照合を行います。"""
        return settings.USERS.get(username) == password

    def create_token(self, username: Username) -> AuthToken:
        """JWT トークンを生成して返します。"""
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode = {
            "sub": username.value,
            "exp": expire,
        }
        token_str = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        return AuthToken(token_str)

    def verify_token(self, token: AuthToken) -> Username | None:
        """JWT トークンを検証し、ユーザー名を返します。"""
        try:
            payload = jwt.decode(
                token.value, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            username_str: str | None = payload.get("sub")
            if username_str is None:
                return None
            return Username(username_str)
        except jwt.PyJWTError:
            return None
