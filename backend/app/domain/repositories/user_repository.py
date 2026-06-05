"""ユーザー情報のリポジトリインターフェース。"""

from typing import Protocol

from app.domain.entities.user import User
from app.domain.primitives.primitives import Username


class UserRepository(Protocol):
    """ユーザーの参照・永続化を行うリポジトリのインターフェース。"""

    async def get_by_username(self, username: Username) -> User | None:
        """指定されたユーザー名に対応するユーザーを取得します。

        存在しない場合は None を返します。
        """
        ...

    async def save(self, user: User) -> User:
        """ユーザー情報を保存または更新します。"""
        ...

    async def get_all(self) -> list[User]:
        """登録されているすべてのユーザーを取得します。"""
        ...
