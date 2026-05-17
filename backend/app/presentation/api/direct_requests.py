"""ダイレクトリクエスト取得の REST API エンドポイント定義。"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, field_validator

from ...application.services.direct_request_service import DirectRequestService
from ...domain.primitives.primitives import EntityId, TaskText, Username
from ...domain.primitives.task_status import TaskStatus
from ..dependencies import get_authenticated_user, get_direct_request_service
from ..websockets.schemas import DirectRequestServerMessage

router = APIRouter(prefix="/api/direct_requests", tags=["direct_requests"])


class UpdateDirectRequestStatusRequest(BaseModel):
    """ステータス更新用のリクエストボディ。

    REST の Body は ``*Request`` で統一する (CONVENTIONS.md 第 1 節)。
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

    REST の Body は ``*Request`` で統一する (CONVENTIONS.md 第 1 節)。
    """

    to: str
    text: str

    def to_domain(self) -> tuple[Username, TaskText]:
        """To / text フィールドをドメインプリミティブへ変換します。"""
        return Username(self.to), TaskText(self.text)


@router.get("")
async def get_requests_since(
    after_id: Annotated[int, Query()],
    username: Annotated[Username, Depends(get_authenticated_user)],
    direct_request_service: Annotated[
        DirectRequestService, Depends(get_direct_request_service)
    ],
) -> list[DirectRequestServerMessage]:
    """
    指定された ID 以降の、自分に関連するすべてのダイレクトリクエストを取得します。
    """
    tasks = await direct_request_service.get_tasks_after(username, EntityId(after_id))
    return [
        DirectRequestServerMessage.from_domain(t, is_history=True)
        for t in tasks
        if t.id is not None
    ]


@router.post("")
async def send_request(
    body: SendDirectRequestRequest,
    username: Annotated[Username, Depends(get_authenticated_user)],
    direct_request_service: Annotated[
        DirectRequestService, Depends(get_direct_request_service)
    ],
) -> dict:
    """ダイレクトリクエストを新規送信します。"""
    recipient, text = body.to_domain()
    await direct_request_service.send_request(username, recipient, text)
    return {"status": "ok"}


@router.patch("/{task_id}/status")
async def update_request_status(
    task_id: int,
    body: UpdateDirectRequestStatusRequest,
    username: Annotated[Username, Depends(get_authenticated_user)],
    direct_request_service: Annotated[
        DirectRequestService, Depends(get_direct_request_service)
    ],
) -> dict:
    """ダイレクトリクエストのステータスを更新します。"""
    await direct_request_service.update_status(
        EntityId(task_id), body.to_domain(), username
    )
    return {"status": "ok"}
