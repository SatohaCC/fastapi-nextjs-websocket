"""ダイレクトリクエストの永続化を抽象化するリポジトリインターフェース。"""

# pylint: disable=unnecessary-ellipsis
from typing import Protocol

from ..entities.direct_request import DirectRequest, DraftDirectRequest
from ..primitives.primitives import EntityId, Username


class RequestRepository(Protocol):
    """ダイレクトリクエストの CRUD 操作を定義するリポジトリインターフェース。"""

    async def save(self, request: DraftDirectRequest) -> DirectRequest:
        """DraftDirectRequest を永続化し、ID 確定済みの DirectRequest を返します。"""
        ...

    async def get_by_id(self, request_id: EntityId) -> DirectRequest | None:
        """IDでリクエストを取得する"""
        ...

    async def get_for_user(self, username: Username) -> list[DirectRequest]:
        """特定のユーザーに関連するリクエストを取得する"""
        ...

    async def get_after(
        self, username: Username, after_id: EntityId
    ) -> list[DirectRequest]:
        """特定のユーザーに関連する、指定ID以降のリクエストを取得する"""
        ...
