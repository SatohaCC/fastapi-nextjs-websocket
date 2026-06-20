"""ユーザー情報のリポジトリインターフェース。"""

from typing import Protocol

from app.domain.entities.user import User
from app.domain.primitives.primitives import UserId, Userid, Username


class UserRepository(Protocol):
    """ユーザーの参照・永続化を行うリポジトリのインターフェース。"""

    async def get_by_id(self, user_id: UserId) -> User | None:
        """指定された ID に対応するユーザーを取得します。

        存在しない場合は None を返します。
        """
        ...

    async def get_by_userid(self, userid: Userid) -> User | None:
        """指定されたログインIDに対応するユーザーを取得します。

        存在しない場合は None を返します。
        """
        ...

    async def save(self, user: User) -> User:
        """ユーザー情報を保存または更新します。"""
        ...

    async def get_all(self) -> list[User]:
        """登録されているすべてのユーザーを取得します。"""
        ...

    async def delete(self, user_id: UserId) -> bool:
        """指定された ID に対応するユーザーを削除します。

        削除に成功した場合は True、存在しなかった場合は False を返します。
        """
        ...

    async def update_username(
        self, user_id: UserId, old_username: Username, new_username: Username
    ) -> None:
        """ユーザーID（ハンドル）を変更し、関連テーブルを一括更新します。"""
        ...
