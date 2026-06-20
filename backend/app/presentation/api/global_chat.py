"""グローバルチャット取得の REST API エンドポイント定義。"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from ...application.services.global_chat_service import GlobalChatService
from ...domain.entities.user import User
from ...domain.primitives.primitives import EntityId, MessageText
from ...infrastructure.rate_limiter import FixedWindowRateLimiter
from ..dependencies import (
    get_authenticated_user,
    get_chat_message_rate_limiter,
    get_global_chat_service,
)
from ..websockets.schemas import GlobalChatServerMessage

router = APIRouter(prefix="/api/global_chat", tags=["global_chat"])


class SendGlobalChatMessageRequest(BaseModel):
    """メッセージ送信用のリクエストボディ。

    REST の Body は ``*Request`` で統一する。
    """

    text: str

    def to_domain(self) -> MessageText:
        """Text フィールドをドメインプリミティブへ変換します。"""
        return MessageText(self.text)


@router.get("/messages")
async def get_messages(
    _: Annotated[User, Depends(get_authenticated_user)],
    global_chat_service: Annotated[GlobalChatService, Depends(get_global_chat_service)],
    after_id: Annotated[int | None, Query()] = None,
    before_id: Annotated[int | None, Query()] = None,
    limit: Annotated[int | None, Query()] = None,
) -> list[GlobalChatServerMessage]:
    """指定された条件（after_id, before_id, limit）に基づいて
    グローバルチャットメッセージを取得します。
    """
    limit_val = limit if limit is not None else 50
    if after_id is not None:
        messages = await global_chat_service.get_messages_after(EntityId(after_id))
    elif before_id is not None:
        messages = await global_chat_service.get_messages_before(
            EntityId(before_id), limit=limit_val
        )
    else:
        messages = await global_chat_service.get_recent_messages(limit=limit_val)
    return [GlobalChatServerMessage.from_domain(m, is_history=True) for m in messages]


@router.post("/messages")
async def send_message(
    body: SendGlobalChatMessageRequest,
    user: Annotated[User, Depends(get_authenticated_user)],
    global_chat_service: Annotated[GlobalChatService, Depends(get_global_chat_service)],
    rate_limiter: Annotated[
        FixedWindowRateLimiter, Depends(get_chat_message_rate_limiter)
    ],
) -> dict:
    """メッセージを新規送信します（REST API 経由）。"""
    if await rate_limiter.is_limited(str(user.id.value)):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="メッセージの送信頻度が高すぎます。しばらく待ってから再試行してください。",
        )
    await global_chat_service.send_message(
        user_id=user.id, username=user.username, text=body.to_domain()
    )
    return {"status": "ok"}
