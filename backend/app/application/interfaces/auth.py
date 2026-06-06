"""認証プロバイダーを抽象化するアプリケーション層インターフェース。"""

from typing import Protocol

from app.domain.primitives.primitives import AuthToken, RefreshToken, UserId


class TokenProvider(Protocol):
    """トークン操作を抽象化したインターフェース。"""

    def create_token(self, user_id: UserId) -> tuple[AuthToken, RefreshToken]:
        """ユーザー ID に基づきトークンペアを生成します。"""
        ...

    def verify_token(self, token: AuthToken) -> UserId | None:
        """アクセストークンを検証し、有効な場合はユーザー ID を返します。"""
        ...

    def verify_refresh_token(self, token: RefreshToken) -> UserId | None:
        """リフレッシュトークンを検証し、有効な場合はユーザー ID を返します。"""
        ...


class TicketStore(Protocol):
    """WebSocketのワンタイムチケットを管理するインターフェース。"""

    async def create_ticket(self, user_id: UserId) -> str:
        """指定されたユーザー ID に対する一時的な接続チケットを生成・保存します。"""
        ...

    async def consume_ticket(self, ticket: str) -> UserId | None:
        """チケットを検証し、有効な場合はユーザー ID を返してチケットを削除します。"""
        ...
