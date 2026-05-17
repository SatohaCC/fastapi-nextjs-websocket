"""統合リカバリ API エンドポイント。"""

from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from ...application.outbox.delivery_feed import DeliveryFeed, SequenceId, SequenceName
from ...application.services.feed_query_service import FeedQueryService
from ...domain.primitives.primitives import Username
from ..dependencies import get_authenticated_user, get_feed_query_service
from ..websockets.schemas import create_server_message_from_feed

router = APIRouter(tags=["Feeds"])


class FeedResponse(BaseModel):
    """フィードレスポンスのスキーマ"""

    sequence_name: str
    sequence_id: int
    event_type: str
    payload: dict[str, Any]
    created_at: datetime

    @classmethod
    def from_domain(cls, feed: DeliveryFeed) -> "FeedResponse":
        """DeliveryFeed エンティティからレスポンス DTO を生成します。"""
        resp_dto = create_server_message_from_feed(feed)
        return cls(
            sequence_name=feed.sequence_name.value,
            sequence_id=feed.sequence_id.value,
            event_type=feed.event_type.value,
            payload=resp_dto.model_dump(mode="json"),
            created_at=feed.created_at,
        )


@router.get("/api/feeds/global_chat", response_model=list[FeedResponse])
async def get_chat_feeds_since(
    username: Annotated[Username, Depends(get_authenticated_user)],
    feed_service: Annotated[FeedQueryService, Depends(get_feed_query_service)],
    after_chat_id: Annotated[
        int, Query(description="この ID 以降のチャットフィードを取得します")
    ] = 0,
) -> list[FeedResponse]:
    """指定された ID 以降のグローバルチャットフィードを取得します（リカバリ用）。"""
    feeds = await feed_service.get_feeds_after(
        SequenceName("global_chat"), SequenceId(after_chat_id), username
    )
    return [
        FeedResponse.from_domain(f)
        for f in feeds
        if f.sequence_name is not None and f.sequence_id is not None
    ]


@router.get("/api/feeds/direct_requests", response_model=list[FeedResponse])
async def get_request_feeds_since(
    username: Annotated[Username, Depends(get_authenticated_user)],
    feed_service: Annotated[FeedQueryService, Depends(get_feed_query_service)],
    after_request_id: Annotated[
        int, Query(description="この ID 以降のリクエストフィードを取得します")
    ] = 0,
) -> list[FeedResponse]:
    """指定された ID 以降のダイレクトリクエストフィードを取得します（リカバリ用）。"""
    feeds = await feed_service.get_feeds_after(
        SequenceName("direct_request"), SequenceId(after_request_id), username
    )
    return [
        FeedResponse.from_domain(f)
        for f in feeds
        if f.sequence_name is not None and f.sequence_id is not None
    ]
