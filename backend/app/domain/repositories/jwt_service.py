from typing import Protocol

from app.domain.primitives.primitives import Username


class JwtService(Protocol):
    """JWT 認証操作を抽象化するインターフェース。"""

    def authenticate_user(self, username: str, password: str) -> bool:
        """ユーザー名とパスワードの照合を行います。"""
        ...

    def create_token(self, username: Username) -> str:
        """JWT トークンを生成して返します。"""
        ...

    def verify_token(self, token: str) -> Username | None:
        """JWT トークンを検証し、ユーザー名を返します。無効な場合は None を返します。"""
        ...
