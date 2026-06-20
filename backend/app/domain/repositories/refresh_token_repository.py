"""リフレッシュトークン情報のリポジトリインターフェース。"""

from datetime import datetime
from typing import Protocol

from app.domain.entities.refresh_token import RefreshToken
from app.domain.primitives.primitives import SessionId, TokenHash, UserId


class RefreshTokenRepository(Protocol):
    """リフレッシュトークンの参照・永続化・削除を行うリポジトリのインターフェース。"""

    async def get_by_id(self, token_id: SessionId) -> RefreshToken | None:
        """指定されたIDに対応するリフレッシュトークンを取得します。

        存在しない場合は None を返します。
        """
        ...

    async def get_by_hash(self, token_hash: TokenHash) -> RefreshToken | None:
        """ハッシュ値に対応するリフレッシュトークンを取得します。

        存在しない場合は None を返します。
        """
        ...

    async def get_by_user_id(self, user_id: UserId) -> list[RefreshToken]:
        """指定されたユーザーに紐づくすべてのリフレッシュトークンを取得します。"""
        ...

    async def save(self, refresh_token: RefreshToken) -> RefreshToken:
        """リフレッシュトークンを保存または更新します。"""
        ...

    async def delete_by_id(self, token_id: SessionId) -> bool:
        """指定されたIDに対応するリフレッシュトークンを物理削除します。"""
        ...

    async def delete_by_hash(self, token_hash: TokenHash) -> bool:
        """ハッシュ値に対応するリフレッシュトークンを物理削除します。

        削除に成功した場合は True、存在しなかった場合は False を返します。
        """
        ...

    async def delete_by_user_id(self, user_id: UserId) -> None:
        """指定されたユーザーに紐づくすべてのリフレッシュトークンを物理削除します。"""
        ...

    async def delete_expired(self, now: datetime) -> int:
        """指定された基準日時より有効期限の古いリフレッシュトークンをすべて物理削除し、削除件数を返します。"""
        ...
