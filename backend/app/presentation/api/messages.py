"""チャットメッセージ取得の REST API エンドポイント定義。"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from ...application.services.chat_service import ChatService
from ...domain.primitives.primitives import EntityId, MessageText, Username
from ..dependencies import get_authenticated_user, get_chat_service
from ..websockets.schemas import ChatResponse

router = APIRouter(prefix="/api", tags=["messages"])


@router.get("/messages")
async def get_messages_since(
    after_id: Annotated[int, Query()],
    _: Annotated[Username, Depends(get_authenticated_user)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> list[ChatResponse]:
    """指定された ID 以降のすべてのチャットメッセージを取得します。"""
    messages = await chat_service.get_messages_after(EntityId(after_id))
    return [
        ChatResponse(
            id=m.id.value,
            username=m.username.value,
            text=m.text.value,
            created_at=m.created_at,
            is_history=True,
        )
        for m in messages
    ]


@router.post("/messages")
async def send_message(
    payload: dict,
    username: Annotated[Username, Depends(get_authenticated_user)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> dict:
    """メッセージを新規送信します（REST API 経由）。"""
    await chat_service.send_message(username, MessageText(payload["text"]))
    return {"status": "ok"}
