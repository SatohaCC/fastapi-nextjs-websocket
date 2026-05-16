"""ダイレクトリクエストに関するユースケースを実現するアプリケーションサービス。"""

from ...domain.entities.task import DraftTask, Task
from ...domain.exceptions import EntityNotFoundException
from ...domain.primitives.primitives import EntityId, TaskText, Username
from ...domain.primitives.task_status import TaskStatus
from ..outbox.delivery_feed import DIRECT_REQUEST_SEQUENCE, DraftDeliveryFeed
from ..outbox.payload import DirectRequestPayload, DirectRequestUpdatePayload
from ..uow import UnitOfWork


class DirectRequestService:
    """ダイレクトリクエストに関するユースケースをまとめたアプリケーションサービス。"""

    def __init__(self, uow: UnitOfWork) -> None:
        """ダイレクトリクエストサービスを初期化します。"""
        self._uow = uow

    async def send_request(
        self, sender: Username, recipient: Username, text: TaskText
    ) -> Task:
        """Task エンティティを生成・保存し、パブリッシュします。"""
        draft = DraftTask(
            sender=sender,
            recipient=recipient,
            text=text,
            status=TaskStatus.REQUESTED,
        )
        async with self._uow:
            saved_task = await self._uow.tasks.save(draft)
            payload = DirectRequestPayload(
                id=saved_task.id,
                sender=saved_task.sender,
                recipient=saved_task.recipient,
                text=saved_task.text,
                status=saved_task.status,
                created_at=saved_task.created_at,
                updated_at=saved_task.updated_at,
            )
            feed = DraftDeliveryFeed(
                sequence_name=DIRECT_REQUEST_SEQUENCE,
                event_type=payload.event_type,
                payload=payload,
            )
            await self._uow.outbox.save(feed)
            await self._uow.commit()

        return saved_task

    async def get_tasks_for_user(self, username: Username) -> list[Task]:
        """ユーザーに関連する Task 履歴を取得します。"""
        async with self._uow:
            return await self._uow.tasks.get_for_user(username)

    async def get_tasks_after(
        self, username: Username, after_id: EntityId
    ) -> list[Task]:
        """指定したID以降のユーザー関連 Task を取得します。"""
        async with self._uow:
            return await self._uow.tasks.get_after(username, after_id)

    async def update_status(
        self, task_id: EntityId, new_status: TaskStatus, operator: Username
    ) -> Task:
        """ステータスを更新し、変更をパブリッシュします。"""
        async with self._uow:
            task = await self._uow.tasks.get_by_id(task_id)
            if not task:
                raise EntityNotFoundException(f"Task {task_id} not found")

            transitioned = task.transition_to(new_status, operator)
            updated_task = await self._uow.tasks.save(transitioned)
            payload = DirectRequestUpdatePayload(
                id=updated_task.id,
                status=updated_task.status,
                sender=updated_task.sender,
                recipient=updated_task.recipient,
                updated_at=updated_task.updated_at,
            )
            feed = DraftDeliveryFeed(
                sequence_name=DIRECT_REQUEST_SEQUENCE,
                event_type=payload.event_type,
                payload=payload,
            )
            await self._uow.outbox.save(feed)
            await self._uow.commit()

        return updated_task
