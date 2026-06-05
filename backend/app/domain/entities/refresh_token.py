"""リフレッシュトークンを表すドメインエンティティ。"""

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
