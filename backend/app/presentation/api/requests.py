"""ダイレクトリクエスト取得の REST API エンドポイント定義。"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, field_validator

from ...application.services.request_service import RequestService
from ...domain.primitives.primitives import EntityId, RequestText, Username
from ...domain.primitives.request_status import RequestStatus
from ..dependencies import get_authenticated_user, get_request_service
from ..websockets.schemas import RequestResponse

router = APIRouter(prefix="/api", tags=["requests"])


class StatusUpdatePayload(BaseModel):
    """ステータス更新用のリクエストボディ。"""

    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """無効なステータス文字列を境界で弾く。"""
        RequestStatus(v)
        return v

    def to_domain(self) -> RequestStatus:
        """Status をドメインプリミティブへ変換します。"""
        return RequestStatus(self.status)


class SendRequestPayload(BaseModel):
    """リクエスト送信用のリクエストボディ。"""

    to: str
    text: str

    def to_domain(self) -> tuple[Username, RequestText]:
        """To / text フィールドをドメインプリミティブへ変換します。"""
        return Username(self.to), RequestText(self.text)


@router.get("/requests")
async def get_requests_since(
    after_id: Annotated[int, Query()],
    username: Annotated[Username, Depends(get_authenticated_user)],
    request_service: Annotated[RequestService, Depends(get_request_service)],
) -> list[RequestResponse]:
    """
    指定された ID 以降の、自分に関連するすべてのダイレクト・リクエストを取得します。
    """
    requests = await request_service.get_requests_after(username, EntityId(after_id))
    return [
        RequestResponse.from_domain(r, is_history=True)
        for r in requests
        if r.id is not None
    ]


@router.post("/requests")
async def send_request(
    payload: SendRequestPayload,
    username: Annotated[Username, Depends(get_authenticated_user)],
    request_service: Annotated[RequestService, Depends(get_request_service)],
) -> dict:
    """ダイレクト・リクエストを新規送信します。"""
    recipient, text = payload.to_domain()
    await request_service.send_request(username, recipient, text)
    return {"status": "ok"}


@router.patch("/requests/{request_id}/status")
async def update_request_status(
    request_id: int,
    payload: StatusUpdatePayload,
    username: Annotated[Username, Depends(get_authenticated_user)],
    request_service: Annotated[RequestService, Depends(get_request_service)],
) -> dict:
    """ダイレクト・リクエストのステータスを更新します。"""
    await request_service.update_status(
        EntityId(request_id), payload.to_domain(), username
    )
    return {"status": "ok"}
