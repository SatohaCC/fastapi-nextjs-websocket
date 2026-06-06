"""ユーザー通知設定の REST API エンドポイント定義。"""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ...application.services.user_settings_service import UserSettingsService
from ...domain.entities.user import User
from ...domain.entities.user_settings import UserSettings
from ..dependencies import get_authenticated_user, get_user_settings_service

router = APIRouter(prefix="/api/user_settings", tags=["user_settings"])


class UserSettingsResponse(BaseModel):
    """通知設定取得のレスポンスボディ。

    REST のレスポンス DTO は ``*Response`` で統一します (CONVENTIONS.md 第 1 節)。
    """

    global_chat: bool
    direct_request: bool
    direct_request_updated: bool
    browser_notification: bool

    @classmethod
    def from_domain(cls, settings: UserSettings) -> "UserSettingsResponse":
        """ドメインエンティティからレスポンススキーマへ変換します。"""
        return cls(
            global_chat=settings.global_chat,
            direct_request=settings.direct_request,
            direct_request_updated=settings.direct_request_updated,
            browser_notification=settings.browser_notification,
        )


class UpdateUserSettingsRequest(BaseModel):
    """通知設定更新用のリクエストボディ。

    REST のリクエストボディ DTO は ``*Request`` で統一します (CONVENTIONS.md 第 1 節)。
    """

    global_chat: bool
    direct_request: bool
    direct_request_updated: bool
    browser_notification: bool


@router.get("", response_model=UserSettingsResponse)
async def get_settings(
    user: Annotated[User, Depends(get_authenticated_user)],
    service: Annotated[UserSettingsService, Depends(get_user_settings_service)],
) -> UserSettingsResponse:
    """現在のユーザーの通知設定を取得します。"""
    settings = await service.get_settings(user.id)
    return UserSettingsResponse.from_domain(settings)


@router.put("", response_model=UserSettingsResponse)
async def update_settings(
    body: UpdateUserSettingsRequest,
    user: Annotated[User, Depends(get_authenticated_user)],
    service: Annotated[UserSettingsService, Depends(get_user_settings_service)],
) -> UserSettingsResponse:
    """現在のユーザーの通知設定を更新します。"""
    settings = await service.update_settings(
        user_id=user.id,
        global_chat=body.global_chat,
        direct_request=body.direct_request,
        direct_request_updated=body.direct_request_updated,
        browser_notification=body.browser_notification,
    )
    return UserSettingsResponse.from_domain(settings)
