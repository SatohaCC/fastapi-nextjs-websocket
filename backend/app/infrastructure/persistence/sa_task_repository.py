"""SQLAlchemy を使用した Task リポジトリの実装。"""

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.task import DraftTask, Task
from ...domain.primitives.primitives import EntityId, TaskText, Username
from ...domain.primitives.task_status import TaskStatus
from ...domain.repositories.task_repository import TaskRepository
from .orm_models import TaskORM


class SqlAlchemyTaskRepository(TaskRepository):
    """SQLAlchemy を使用した TaskRepository の実装。"""

    def __init__(self, session: AsyncSession):
        """SQLAlchemy セッションを初期化します。"""
        self._session = session

    async def save(self, task: DraftTask) -> Task:
        """エンティティを DB に保存（新規作成または更新）します。"""
        orm = TaskORM(
            sender=task.sender.value,
            recipient=task.recipient.value,
            text=task.text.value,
            status=task.status.value,
            created_at=task.created_at,
            updated_at=task.updated_at if isinstance(task, Task) else task.created_at,
        )
        if isinstance(task, Task):
            orm.id = task.id.value
            orm = await self._session.merge(orm)
        else:
            self._session.add(orm)

        # Note: commit() は UoW が担当するため、ここでは行わない
        await self._session.flush()
        await self._session.refresh(orm)
        return self._to_entity(orm)

    async def get_by_id(self, task_id: EntityId) -> Task | None:
        """ID で Task を検索します。"""
        res = await self._session.execute(
            select(TaskORM).where(TaskORM.id == task_id.value)
        )
        orm = res.scalar_one_or_none()
        return self._to_entity(orm) if orm else None

    async def get_for_user(self, username: Username) -> list[Task]:
        """ユーザーに関連する Task を全件取得します（送信、受信の両方）。"""
        stmt = (
            select(TaskORM)
            .where(
                or_(
                    TaskORM.sender == username.value,
                    TaskORM.recipient == username.value,
                )
            )
            .order_by(TaskORM.created_at.asc())
        )
        res = await self._session.execute(stmt)
        return [self._to_entity(row) for row in res.scalars().all()]

    async def get_after(self, username: Username, after_id: EntityId) -> list[Task]:
        """指定したID以降のユーザー関連 Task を取得します。"""
        stmt = (
            select(TaskORM)
            .where(
                or_(
                    TaskORM.sender == username.value,
                    TaskORM.recipient == username.value,
                ),
                TaskORM.id > after_id.value,
            )
            .order_by(TaskORM.id.asc())
        )
        res = await self._session.execute(stmt)
        return [self._to_entity(row) for row in res.scalars().all()]

    def _to_entity(self, orm: TaskORM) -> Task:
        """ORM モデルをドメインエンティティに変換します。"""
        return Task(
            id=EntityId(orm.id),
            sender=Username(orm.sender),
            recipient=Username(orm.recipient),
            text=TaskText(orm.text),
            status=TaskStatus(orm.status),
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )
