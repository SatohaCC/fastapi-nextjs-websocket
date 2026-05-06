"""ダイレクトリクエストに関するユースケースを実現するアプリケーションサービス。"""

from app.domain.primitives.feed import SequenceName

from ...domain.entities.delivery_feed import DeliveryFeed
from ...domain.entities.direct_request import DirectRequest
from ...domain.exceptions import EntityNotFoundException
from ...domain.factories.delivery_feed_factory import DeliveryFeedFactory
from ...domain.primitives.primitives import EntityId, RequestText, Username
from ...domain.primitives.request_status import RequestStatus
from ..uow import UnitOfWork


class RequestService:
    """ダイレクト・リクエストに関するユースケースをまとめたアプリケーションサービス。"""

    def __init__(self, uow: UnitOfWork) -> None:
        """リクエストサービスを初期化します。"""
        self._uow = uow

    async def send_request(
        self, sender: Username, recipient: Username, text: RequestText
    ) -> DirectRequest:
        """リクエストエンティティを生成・保存し、パブリッシュします。"""
        request = DirectRequest(
            sender=sender,
            recipient=recipient,
            text=text,
            status=RequestStatus.REQUESTED,
        )
        async with self._uow:
            saved_request = await self._uow.requests.save(request)

            event_type, payload = DeliveryFeedFactory.create_payload_from_request(
                saved_request
            )
            feed = DeliveryFeed(
                sequence_name=SequenceName("requests_global"),
                event_type=event_type,
                payload=payload,
            )
            await self._uow.outbox.save(feed)

            await self._uow.commit()

        return saved_request

    async def get_requests_for_user(self, username: Username) -> list[DirectRequest]:
        """ユーザーに関連するリクエスト履歴を取得します。"""
        async with self._uow:
            return await self._uow.requests.get_for_user(username)

    async def get_requests_after(
        self, username: Username, after_id: EntityId
    ) -> list[DirectRequest]:
        """指定したID以降のユーザー関連リクエストを取得します。"""
        async with self._uow:
            return await self._uow.requests.get_after(username, after_id)

    async def update_status(
        self, request_id: EntityId, new_status: RequestStatus, operator: Username
    ) -> DirectRequest:
        """ステータスを更新し、変更をパブリッシュします。"""
        async with self._uow:
            request = await self._uow.requests.get_by_id(request_id)
            if not request:
                raise EntityNotFoundException(f"Request {request_id} not found")

            # ステータス遷移（内部でバリデーション、権限チェック、時刻更新が行われる）
            request.transition_to(new_status, operator)

            updated_request = await self._uow.requests.save(request)

            event_type, payload = (
                DeliveryFeedFactory.create_payload_from_request_updated(updated_request)
            )
            feed = DeliveryFeed(
                sequence_name=SequenceName("requests_global"),
                event_type=event_type,
                payload=payload,
            )
            await self._uow.outbox.save(feed)

            await self._uow.commit()

        return updated_request
