"""リフレッシュトークンを表すドメインエンティティ。"""

import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime

from app.domain.primitives.primitives import UserId


@dataclass(frozen=True, kw_only=True)
class RefreshToken:
    """リフレッシュトークン情報を表現するエンティティ。"""

    id: uuid.UUID
    user_id: UserId
    token_hash: str
    expires_at: datetime
    created_at: datetime
    ip_address: str | None = None
    user_agent: str | None = None

    @staticmethod
    def hash_token(token: str) -> str:
        """トークン文字列を SHA-256 でハッシュ化して 16 進数文字列を返します。"""
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @classmethod
    def create(
        cls,
        *,
        id: uuid.UUID,
        user_id: UserId,
        token_value: str,
        expires_at: datetime,
        created_at: datetime,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> "RefreshToken":
        """新しいリフレッシュトークンエンティティを生成します。"""
        return cls(
            id=id,
            user_id=user_id,
            token_hash=cls.hash_token(token_value),
            expires_at=expires_at,
            created_at=created_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )
