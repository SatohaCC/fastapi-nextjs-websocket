"""リフレッシュトークンを表すドメインエンティティ。"""

import hashlib
from dataclasses import dataclass
from datetime import datetime

from app.domain.primitives.primitives import (
    IpAddress,
    SessionId,
    TokenHash,
    UserAgent,
    UserId,
)


@dataclass(frozen=True, kw_only=True)
class RefreshToken:
    """リフレッシュトークン情報を表現するエンティティ。"""

    id: SessionId
    user_id: UserId
    token_hash: TokenHash
    expires_at: datetime
    created_at: datetime
    ip_address: IpAddress | None = None
    user_agent: UserAgent | None = None

    @staticmethod
    def hash_token(token: str) -> TokenHash:
        """トークン文字列を SHA-256 でハッシュ化して TokenHash を返します。"""
        return TokenHash(hashlib.sha256(token.encode("utf-8")).hexdigest())

    @classmethod
    def create(
        cls,
        *,
        id: SessionId,
        user_id: UserId,
        token_value: str,
        expires_at: datetime,
        created_at: datetime,
        ip_address: IpAddress | None = None,
        user_agent: UserAgent | None = None,
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
