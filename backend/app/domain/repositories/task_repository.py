"""Task の永続化を抽象化するリポジトリインターフェース。"""

# pylint: disable=unnecessary-ellipsis
from typing import Protocol

from ..entities.task import DraftTask, Task
from ..primitives.primitives import EntityId, UserId


class TaskRepository(Protocol):
    """Task の CRUD 操作を定義するリポジトリインターフェース。"""

    async def save(self, task: DraftTask) -> Task:
        """DraftTask を永続化し、ID 確定済みの Task を返します。"""
        ...

    async def get_by_id(self, task_id: EntityId) -> Task | None:
        """ID で Task を取得する"""
        ...

    async def get_for_user(self, user_id: UserId) -> list[Task]:
        """特定のユーザーに関連する Task を取得する"""
        ...

    async def get_after(self, user_id: UserId, after_id: EntityId) -> list[Task]:
        """特定のユーザーに関連する、指定ID以降の Task を取得する"""
        ...
