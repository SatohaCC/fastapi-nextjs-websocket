"""ユーザーを表すドメインエンティティ。"""

from dataclasses import dataclass

from app.domain.primitives.primitives import Username


@dataclass(frozen=True, kw_only=True)
class User:
    """システム内のユーザー情報を表現するエンティティ。"""

    username: Username
    hashed_password: str
