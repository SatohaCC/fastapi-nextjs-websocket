"""アプリケーション層のトランザクション境界を定義する Unit of Work インターフェース。"""

from typing import Protocol

from ..domain.repositories.message_repository import MessageRepository
from ..domain.repositories.task_repository import TaskRepository
from .outbox.repository import DeliveryFeedRepository


class UnitOfWork(Protocol):
    """アプリケーション層でトランザクション境界を管理するためのインターフェース。
    リポジトリへのアクセスポイント（Repository Accessor）も提供します。
    """

    tasks: TaskRepository
    messages: MessageRepository
    outbox: DeliveryFeedRepository

    async def commit(self) -> None:
        """トランザクションを確定します。"""

    async def rollback(self) -> None:
        """トランザクションを取り消します。"""

    async def __aenter__(self) -> "UnitOfWork":
        """コンテキストの開始。"""
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """コンテキストの終了。"""
        ...
