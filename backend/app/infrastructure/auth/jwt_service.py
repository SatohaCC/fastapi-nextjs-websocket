"""PyJWT を使用した JWT 認証サービスの実装。"""

from datetime import datetime, timedelta, timezone

import jwt

from app.domain.primitives.primitives import Username

from ..config import settings


class JwtServiceImpl:
    """JwtService の実装。PyJWT を使用します。"""

    def authenticate_user(self, username: str, password: str) -> bool:
        """ユーザー名とパスワードの照合を行います。"""
        return settings.USERS.get(username) == password

    def create_token(self, username: Username) -> str:
        """JWT トークンを生成して返します。"""
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode = {"sub": username.value, "exp": expire}
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def verify_token(self, token: str) -> Username | None:
        """JWT トークンを検証し、ユーザー名を返します。"""
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            username_str: str | None = payload.get("sub")
            if username_str is None:
                return None
            return Username(username_str)
        except jwt.PyJWTError:
            return None
