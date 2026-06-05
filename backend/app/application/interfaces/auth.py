"""認証プロバイダーを抽象化するアプリケーション層インターフェース。"""

from typing import Protocol

from app.domain.primitives.primitives import AuthToken, RefreshToken, Username


class TokenProvider(Protocol):
    """トークン操作を抽象化したインターフェース。"""

    def create_token(self, username: Username) -> tuple[AuthToken, RefreshToken]:
        """ユーザー名に基づきアクセストークンとリフレッシュトークンのペアを生成します。"""
        ...

    def verify_token(self, token: AuthToken) -> Username | None:
        """アクセストークンを検証し、有効な場合はユーザー名を返します。"""
        ...

    def verify_refresh_token(self, token: RefreshToken) -> Username | None:
        """リフレッシュトークンを検証し、有効な場合はユーザー名を返します。"""
        ...


class TicketStore(Protocol):
    """WebSocketのワンタイムチケットを管理するインターフェース。"""

    async def create_ticket(self, username: Username) -> str:
        """指定されたユーザーに対する一時的な接続チケットを生成・保存します。"""
        ...

    async def consume_ticket(self, ticket: str) -> Username | None:
        """チケットを検証し、有効な場合は対応するユーザー名を返し、チケットを即時削除します。"""
        ...
