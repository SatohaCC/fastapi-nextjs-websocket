"""グローバルチャット取得の REST API エンドポイント定義。"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from ...application.services.global_chat_service import GlobalChatService
from ...domain.primitives.primitives import EntityId, MessageText, Username
from ..dependencies import get_authenticated_user, get_global_chat_service
from ..websockets.schemas import GlobalChatResponse

router = APIRouter(prefix="/api/global_chat", tags=["global_chat"])


class SendGlobalChatMessageRequest(BaseModel):
    """メッセージ送信用のリクエストボディ。

    REST の Body は ``*Request`` で統一する (CONVENTIONS.md 第 1 節)。
    """

    text: str

    def to_domain(self) -> MessageText:
        """Text フィールドをドメインプリミティブへ変換します。"""
        return MessageText(self.text)


@router.get("/messages")
async def get_messages_since(
    after_id: Annotated[int, Query()],
    _: Annotated[Username, Depends(get_authenticated_user)],
    global_chat_service: Annotated[GlobalChatService, Depends(get_global_chat_service)],
) -> list[GlobalChatResponse]:
    """指定された ID 以降のすべてのグローバルチャットメッセージを取得します。"""
    messages = await global_chat_service.get_messages_after(EntityId(after_id))
    return [GlobalChatResponse.from_domain(m, is_history=True) for m in messages]


@router.post("/messages")
async def send_message(
    body: SendGlobalChatMessageRequest,
    username: Annotated[Username, Depends(get_authenticated_user)],
    global_chat_service: Annotated[GlobalChatService, Depends(get_global_chat_service)],
) -> dict:
    """メッセージを新規送信します（REST API 経由）。"""
    await global_chat_service.send_message(username, body.to_domain())
    return {"status": "ok"}
