"""ダイレクトリクエストに関するユースケースを実現するアプリケーションサービス。"""

from ...domain.entities.task import DraftTask, Task
from ...domain.exceptions import EntityNotFoundException
from ...domain.primitives.primitives import EntityId, TaskText, UserId, Userid, Username
from ...domain.primitives.task_status import TaskStatus
from ..outbox.delivery_feed import DraftDeliveryFeed, direct_request_sequence
from ..outbox.payload import (
    DirectRequestPayload,
    DirectRequestUpdatePayload,
    FeedPayload,
)
from ..uow import UnitOfWork


class DirectRequestService:
    """ダイレクトリクエストに関するユースケースをまとめたアプリケーションサービス。

    Note:
        内部では ``Task`` エンティティを使用する (``Task`` ≒ DirectRequest)。
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """ダイレクトリクエストサービスを初期化します。"""
        self._uow = uow

    async def _fanout_to_inboxes(
        self, payload: FeedPayload, sender_userid: Userid, recipient_userid: Userid
    ) -> None:
        """DM ペイロードを関係者（sender / recipient）の inbox へ複製保存します。

        受信者ごとに独立した連番（``direct_request:{userid}``）で採番することで、
        各クライアントは自分の inbox の seq だけを連番として追える。自分宛
        （sender == recipient）の場合は重複を除いて 1 件のみ保存する。
        """
        for target in {sender_userid.value, recipient_userid.value}:
            feed = DraftDeliveryFeed(
                sequence_name=direct_request_sequence(target),
                event_type=payload.event_type,
                payload=payload,
            )
            await self._uow.outbox.save(feed)

    async def send_request(
        self,
        sender_id: UserId,
        sender: Username,
        recipient_id: UserId,
        text: TaskText,
    ) -> Task:
        """Task エンティティを生成・保存し、パブリッシュします。"""
        async with self._uow:
            recipient_user = await self._uow.users.get_by_id(recipient_id)
            if recipient_user is None:
                raise EntityNotFoundException(f"User '{recipient_id.value}' not found")

            sender_user = await self._uow.users.get_by_id(sender_id)
            if sender_user is None:
                raise EntityNotFoundException("Sender user not found")

            draft = DraftTask(
                sender_id=sender_id,
                recipient_id=recipient_user.id,
                sender=sender_user.username,
                recipient=recipient_user.username,
                text=text,
                status=TaskStatus.REQUESTED,
            )
            saved_task = await self._uow.tasks.save(draft)
            payload = DirectRequestPayload(
                id=saved_task.id,
                sender_id=saved_task.sender_id,
                recipient_id=saved_task.recipient_id,
                sender_userid=sender_user.userid,
                recipient_userid=recipient_user.userid,
                sender=saved_task.sender,
                recipient=saved_task.recipient,
                text=saved_task.text,
                status=saved_task.status,
                created_at=saved_task.created_at,
                updated_at=saved_task.updated_at,
            )
            await self._fanout_to_inboxes(
                payload, sender_user.userid, recipient_user.userid
            )
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

    async def get_recent_tasks(self, user_id: UserId, limit: int = 50) -> list[Task]:
        """最新のユーザー関連 Task を取得します。"""
        async with self._uow:
            return await self._uow.tasks.get_recent(user_id, limit)

    async def get_tasks_before(
        self, user_id: UserId, before_id: EntityId, limit: int = 50
    ) -> list[Task]:
        """指定したID以前のユーザー関連 Task を取得します。"""
        async with self._uow:
            return await self._uow.tasks.get_before(user_id, before_id, limit)

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

            sender_user = await self._uow.users.get_by_id(updated_task.sender_id)
            recipient_user = await self._uow.users.get_by_id(updated_task.recipient_id)
            if sender_user is None or recipient_user is None:
                raise EntityNotFoundException("User not found for task update fanout")

            payload = DirectRequestUpdatePayload(
                id=updated_task.id,
                status=updated_task.status,
                sender_id=updated_task.sender_id,
                recipient_id=updated_task.recipient_id,
                sender_userid=sender_user.userid,
                recipient_userid=recipient_user.userid,
                sender=updated_task.sender,
                recipient=updated_task.recipient,
                updated_at=updated_task.updated_at,
            )
            await self._fanout_to_inboxes(
                payload, sender_user.userid, recipient_user.userid
            )
            await self._uow.commit()

        return updated_task
