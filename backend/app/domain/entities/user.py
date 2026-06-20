"""ユーザーを表すドメインエンティティ。"""

from dataclasses import dataclass

from app.domain.primitives.primitives import (
    HashedPassword,
    UserId,
    Userid,
    Username,
)


@dataclass(frozen=True, kw_only=True)
class User:
    """システム内のユーザー情報を表現するエンティティ。"""

    id: UserId
    userid: Userid
    username: Username
    hashed_password: HashedPassword
