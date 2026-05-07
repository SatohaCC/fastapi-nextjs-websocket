"""チャットメッセージの永続化を抽象化するリポジトリインターフェース。"""

# pylint: disable=unnecessary-ellipsis
from typing import Protocol

from ..entities.message import DraftMessage, Message
from ..primitives.primitives import EntityId


class MessageRepository(Protocol):
    """チャットメッセージの CRUD 操作を定義するリポジトリインターフェース。"""

    async def save(self, message: DraftMessage) -> Message:
        """DraftMessage を永続化し、ID が確定した Message を返します。"""
        ...

    async def get_after(self, after_id: EntityId) -> list[Message]:
        """指定された ID よりも後のメッセージを昇順で取得します。
        主に接続後の差分更新に使用されます。
        """
        ...

    async def get_recent(self, limit: int = 50) -> list[Message]:
        """最新のメッセージを指定された件数分、昇順で取得します。"""
        ...
