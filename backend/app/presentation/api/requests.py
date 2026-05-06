"""ダイレクトリクエスト取得の REST API エンドポイント定義。"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from pydantic import BaseModel
from ...application.services.request_service import RequestService
from ...domain.primitives.request_status import RequestStatus
from ..dependencies import get_authenticated_user, get_request_service
from ..websockets.schemas import RequestResponse

router = APIRouter(prefix="/api", tags=["requests"])


class StatusUpdatePayload(BaseModel):
    """ステータス更新用のリクエストボディ。"""
    status: RequestStatus


@router.get("/requests")
async def get_requests_since(
    after_id: Annotated[int, Query()],
    username: Annotated[str, Depends(get_authenticated_user)],
    request_service: Annotated[RequestService, Depends(get_request_service)],
) -> list[RequestResponse]:
    """
    指定された ID 以降の、自分に関連するすべてのダイレクト・リクエストを取得します。
    """
    requests = await request_service.get_requests_after(username, after_id)
    return [
        RequestResponse(
            id=r.id.value,
            sender=r.sender.value,
            recipient=r.recipient.value,
            text=r.text.value,
            status=r.status,
            created_at=r.created_at,
            updated_at=r.updated_at,
            is_history=True,
        )
        for r in requests
        if r.id is not None
    ]

@router.post("/requests")
async def send_request(
    payload: dict,
    username: Annotated[str, Depends(get_authenticated_user)],
    request_service: Annotated[RequestService, Depends(get_request_service)],
) -> dict:
    """ダイレクト・リクエストを新規送信します。"""
    await request_service.send_request(username, payload["to"], payload["text"])
    return {"status": "ok"}

@router.patch("/requests/{request_id}/status")
async def update_request_status(
    request_id: int,
    payload: StatusUpdatePayload,
    username: Annotated[str, Depends(get_authenticated_user)],
    request_service: Annotated[RequestService, Depends(get_request_service)],
) -> dict:
    """ダイレクト・リクエストのステータスを更新します。"""
    await request_service.update_status(request_id, payload.status, username)
    return {"status": "ok"}
