"""ダイレクトリクエストに関するユースケースを実現するアプリケーションサービス。"""

from ...domain.entities.task import DraftTask, Task
from ...domain.exceptions import EntityNotFoundException
from ...domain.primitives.primitives import EntityId, TaskText, UserId, Username
from ...domain.primitives.task_status import TaskStatus
from ..outbox.delivery_feed import DIRECT_REQUEST_SEQUENCE, DraftDeliveryFeed
from ..outbox.payload import DirectRequestPayload, DirectRequestUpdatePayload
from ..uow import UnitOfWork


class DirectRequestService:
    """ダイレクトリクエストに関するユースケースをまとめたアプリケーションサービス。

    Note:
        内部では ``Task`` エンティティを使用する (``Task`` ≒ DirectRequest)。
        詳細は CONVENTIONS.md 第 6 節を参照。
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """ダイレクトリクエストサービスを初期化します。"""
        self._uow = uow

    async def send_request(
        self,
        sender_id: UserId,
        sender: Username,
        recipient: Username,
        text: TaskText,
    ) -> Task:
        """Task エンティティを生成・保存し、パブリッシュします。

        recipient の UserId は username で検索して解決します。
        """
        async with self._uow:
            recipient_user = await self._uow.users.get_by_username(recipient)
            if recipient_user is None:
                raise EntityNotFoundException(f"User '{recipient.value}' not found")

            draft = DraftTask(
                sender_id=sender_id,
                recipient_id=recipient_user.id,
                sender=sender,
                recipient=recipient,
                text=text,
                status=TaskStatus.REQUESTED,
            )
            saved_task = await self._uow.tasks.save(draft)
            payload = DirectRequestPayload(
                id=saved_task.id,
                sender_id=saved_task.sender_id,
                recipient_id=saved_task.recipient_id,
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

    async def get_tasks_for_user(self, user_id: UserId) -> list[Task]:
        """ユーザーに関連する Task 履歴を取得します。"""
        async with self._uow:
            return await self._uow.tasks.get_for_user(user_id)

    async def get_tasks_after(self, user_id: UserId, after_id: EntityId) -> list[Task]:
        """指定したID以降のユーザー関連 Task を取得します。"""
        async with self._uow:
            return await self._uow.tasks.get_after(user_id, after_id)

    async def update_status(
        self, task_id: EntityId, new_status: TaskStatus, operator_id: UserId
    ) -> Task:
        """ステータスを更新し、変更をパブリッシュします。"""
        async with self._uow:
            task = await self._uow.tasks.get_by_id(task_id)
            if not task:
                raise EntityNotFoundException(f"Task {task_id} not found")

            transitioned = task.transition_to(new_status, operator_id)
            updated_task = await self._uow.tasks.save(transitioned)
            payload = DirectRequestUpdatePayload(
                id=updated_task.id,
                status=updated_task.status,
                sender_id=updated_task.sender_id,
                recipient_id=updated_task.recipient_id,
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
