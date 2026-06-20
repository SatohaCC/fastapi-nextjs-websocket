"""認証関連のインターフェース定義。"""

import uuid
from typing import Protocol

from app.domain.primitives.primitives import (
    AuthToken,
    RefreshToken,
    SessionId,
    UserId,
)


class TokenProvider(Protocol):
    """トークン操作を抽象化したインターフェース。"""

    def create_token(
        self, user_id: UserId, session_id: uuid.UUID | None = None
    ) -> tuple[AuthToken, RefreshToken]:
        """ユーザー ID とセッション ID に基づきトークンペアを生成します。"""
        ...

    def verify_token(self, token: AuthToken) -> UserId | None:
        """アクセストークンを検証し、有効な場合はユーザー ID を返します。"""
        ...

    def verify_refresh_token(self, token: RefreshToken) -> UserId | None:
        """リフレッシュトークンを検証し、有効な場合はユーザー ID を返します。"""
        ...

    def get_session_id_from_token(self, token: AuthToken) -> uuid.UUID | None:
        """アクセストークンからセッション ID (sid) を取得します。"""
        ...


class TicketStore(Protocol):
    """WebSocketのワンタイムチケットを管理するインターフェース。"""

    async def create_ticket(
        self, user_id: UserId, session_id: SessionId | None = None
    ) -> str:
        """指定されたユーザー ID（とセッション ID）に対する
        一時的な接続チケットを生成・保存します。
        """
        ...

    async def consume_ticket(
        self, ticket: str
    ) -> tuple[UserId, SessionId | None] | None:
        """チケットを検証し、有効な場合は
        (ユーザー ID, セッション ID) を返してチケットを削除します。
        """
        ...
