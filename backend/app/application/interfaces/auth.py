"""認証プロバイダーを抽象化するアプリケーション層インターフェース。"""

from typing import Protocol


class TokenProvider(Protocol):
    """認証（パスワード検証）とトークン操作を抽象化したインターフェース。"""

    def authenticate(self, username: str, password: str) -> bool:
        """ユーザー名とパスワードを検証します。"""
        ...

    def create_token(self, username: str) -> str:
        """ユーザー名に基づきアクセス・トークンを生成します。"""
        ...

    def verify_token(self, token: str) -> str | None:
        """トークンを検証し、有効な場合はユーザー名を返します。"""
        ...
