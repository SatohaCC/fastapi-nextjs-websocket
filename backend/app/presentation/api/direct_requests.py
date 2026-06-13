"""ダイレクトリクエスト取得の REST API エンドポイント定義。"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, field_validator

from ...application.services.direct_request_service import DirectRequestService
from ...domain.entities.user import User
from ...domain.primitives.primitives import EntityId, TaskText, Username
from ...domain.primitives.task_status import TaskStatus
from ...infrastructure.rate_limiter import FixedWindowRateLimiter
from ..dependencies import (
    get_authenticated_user,
    get_direct_request_rate_limiter,
    get_direct_request_service,
    get_status_update_rate_limiter,
)
from ..websockets.schemas import DirectRequestServerMessage

router = APIRouter(prefix="/api/direct_requests", tags=["direct_requests"])


class UpdateDirectRequestStatusRequest(BaseModel):
    """ステータス更新用のリクエストボディ。

    REST の Body は ``*Request`` で統一する。
    ``*Payload`` は DeliveryFeed のイベントペイロード専用語であり、ここでは使わない。
    """

    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """無効なステータス文字列を境界で弾く。"""
        TaskStatus(v)
        return v

    def to_domain(self) -> TaskStatus:
        """Status をドメインプリミティブへ変換します。"""
        return TaskStatus(self.status)


class SendDirectRequestRequest(BaseModel):
    """ダイレクトリクエスト送信用のリクエストボディ。

    REST の Body は ``*Request`` で統一する。
    """

    to: str
    text: str

    def to_domain(self) -> tuple[Username, TaskText]:
        """To / text フィールドをドメインプリミティブへ変換します。"""
        return Username(self.to), TaskText(self.text)


@router.get("")
async def get_requests_since(
    after_id: Annotated[int, Query()],
    user: Annotated[User, Depends(get_authenticated_user)],
    direct_request_service: Annotated[
        DirectRequestService, Depends(get_direct_request_service)
    ],
) -> list[DirectRequestServerMessage]:
    """
    指定された ID 以降の、自分に関連するすべてのダイレクトリクエストを取得します。
    """
    tasks = await direct_request_service.get_tasks_after(user.id, EntityId(after_id))
    return [
        DirectRequestServerMessage.from_domain(t, is_history=True)
        for t in tasks
        if t.id is not None
    ]


@router.post("")
async def send_request(
    body: SendDirectRequestRequest,
    user: Annotated[User, Depends(get_authenticated_user)],
    direct_request_service: Annotated[
        DirectRequestService, Depends(get_direct_request_service)
    ],
    rate_limiter: Annotated[
        FixedWindowRateLimiter, Depends(get_direct_request_rate_limiter)
    ],
) -> dict:
    """ダイレクトリクエストを新規送信します。"""
    if await rate_limiter.is_limited(str(user.id.value)):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="リクエストの送信頻度が高すぎます。しばらく待ってから再試行してください。",
        )
    recipient, text = body.to_domain()
    await direct_request_service.send_request(
        sender_id=user.id,
        sender=user.username,
        recipient=recipient,
        text=text,
    )
    return {"status": "ok"}


@router.patch("/{task_id}/status")
async def update_request_status(
    task_id: int,
    body: UpdateDirectRequestStatusRequest,
    user: Annotated[User, Depends(get_authenticated_user)],
    direct_request_service: Annotated[
        DirectRequestService, Depends(get_direct_request_service)
    ],
    rate_limiter: Annotated[
        FixedWindowRateLimiter, Depends(get_status_update_rate_limiter)
    ],
) -> dict:
    """ダイレクトリクエストのステータスを更新します。"""
    if await rate_limiter.is_limited(str(user.id.value)):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="ステータス更新の頻度が高すぎます。しばらく待ってから再試行してください。",
        )
    await direct_request_service.update_status(
        EntityId(task_id), body.to_domain(), user.id
    )
    return {"status": "ok"}
