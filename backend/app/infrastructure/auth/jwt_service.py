"""PyJWT を使用した JWT 認証サービスの実装。"""

from datetime import datetime, timedelta, timezone

import jwt

from ..config import settings


class JwtServiceImpl:
    """JwtService の実装。PyJWT を使用します。"""

    def authenticate_user(self, username: str, password: str) -> bool:
        """ユーザー名とパスワードの照合を行います。"""
        return settings.USERS.get(username) == password

    def create_token(self, username: str) -> str:
        """JWT トークンを生成して返します。"""
        payload = {
            "sub": username,
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES),
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def verify_token(self, token: str) -> str | None:
        """JWT トークンを検証し、ユーザー名を返します。無効な場合は None を返します。"""
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return payload.get("sub")
        except jwt.InvalidTokenError:
            return None
