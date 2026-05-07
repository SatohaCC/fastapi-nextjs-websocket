"""認証プロバイダーを抽象化するアプリケーション層インターフェース。"""

from typing import Protocol

from app.domain.primitives.primitives import AuthToken, Password, Username


class TokenProvider(Protocol):
    """認証（パスワード検証）とトークン操作を抽象化したインターフェース。"""

    def authenticate(self, username: Username, password: Password) -> bool:
        """ユーザー名とパスワードを検証します。"""
        ...

    def create_token(self, username: Username) -> AuthToken:
        """ユーザー名に基づきアクセス・トークンを生成します。"""
        ...

    def verify_token(self, token: AuthToken) -> Username | None:
        """トークンを検証し、有効な場合はユーザー名を返します。"""
        ...
