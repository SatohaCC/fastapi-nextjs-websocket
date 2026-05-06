"""認証関連の REST API エンドポイント定義。"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ...application.services.auth_service import AuthService
from ..dependencies import get_auth_service, get_authenticated_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    """ログインリクエスト用のスキーマ"""

    username: str
    password: str


class LoginResponse(BaseModel):
    """ログインレスポンス用のスキーマ"""

    access_token: str
    token_type: str


class MeResponse(BaseModel):
    """ユーザー情報レスポンス用のスキーマ"""

    username: str


@router.post("/token")
async def login(
    body: LoginRequest, auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> LoginResponse:
    """認証を行い、アクセストークンを発行します。"""
    token = auth_service.login(body.username, body.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが正しくありません",
        )
    return LoginResponse(access_token=token, token_type="bearer")


@router.get("/me")
async def me(username: Annotated[str, Depends(get_authenticated_user)]) -> MeResponse:
    """現在のログインユーザー情報を取得します。"""
    return MeResponse(username=username)


@router.get("/users")
async def list_users(
    _: Annotated[str, Depends(get_authenticated_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> list[str]:
    """システムに登録されているユーザー一覧を取得します。"""
    return auth_service.get_all_usernames()
