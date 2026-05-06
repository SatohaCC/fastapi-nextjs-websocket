"""統合リカバリ API エンドポイント。"""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from ...application.services.feed_query_service import FeedQueryService
from ...domain.primitives.feed import SequenceId, SequenceName
from ...domain.primitives.primitives import Username
from ..dependencies import get_authenticated_user, get_feed_query_service

router = APIRouter(tags=["Feeds"])


class FeedResponse(BaseModel):
    """フィードレスポンスのスキーマ"""

    sequence_name: str
    sequence_id: int
    event_type: str
    payload: dict
    created_at: datetime


@router.get("/api/feeds", response_model=list[FeedResponse])
async def get_feeds_since(
    username: Annotated[Username, Depends(get_authenticated_user)],
    feed_service: Annotated[FeedQueryService, Depends(get_feed_query_service)],
    after_chat_id: Annotated[
        int | None, Query(description="この ID 以降のチャットフィードを取得します")
    ] = None,
    after_request_id: Annotated[
        int | None, Query(description="この ID 以降のリクエストフィードを取得します")
    ] = None,
) -> list[FeedResponse]:
    """指定された ID 以降のフィードを取得します（リカバリ用）。"""
    feeds = []

    if after_chat_id is not None:
        chat_feeds = await feed_service.get_feeds_after(
            SequenceName("chat_global"), SequenceId(after_chat_id), username
        )
        feeds.extend(chat_feeds)

    if after_request_id is not None:
        request_feeds = await feed_service.get_feeds_after(
            SequenceName("requests_global"), SequenceId(after_request_id), username
        )
        feeds.extend(request_feeds)

    return [
        FeedResponse(
            sequence_name=f.sequence_name.value,
            sequence_id=f.sequence_id.value,
            event_type=f.event_type.value,
            payload=f.payload,
            created_at=f.created_at,
        )
        for f in feeds
        if f.sequence_name is not None and f.sequence_id is not None
    ]
