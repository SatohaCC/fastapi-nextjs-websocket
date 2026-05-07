"""認証関連の REST API エンドポイント定義。"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ...application.services.auth_service import AuthService
from ...domain.primitives.primitives import AuthToken, Password, Username
from ..dependencies import get_auth_service, get_authenticated_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    """ログインリクエスト用のスキーマ"""

    username: str
    password: str

    def to_domain(self) -> tuple[Username, Password]:
        """フィールドをドメインプリミティブへ変換します。"""
        return Username(self.username), Password(self.password)


class LoginResponse(BaseModel):
    """ログインレスポンス用のスキーマ"""

    access_token: str
    token_type: str

    @classmethod
    def from_domain(cls, token: AuthToken) -> "LoginResponse":
        """AuthToken ドメインプリミティブからレスポンス DTO を生成します。"""
        return cls(access_token=token.value, token_type="bearer")


class MeResponse(BaseModel):
    """ユーザー情報レスポンス用のスキーマ"""

    username: str

    @classmethod
    def from_domain(cls, username: Username) -> "MeResponse":
        """Username ドメインプリミティブからレスポンス DTO を生成します。"""
        return cls(username=username.value)


@router.post("/token")
async def login(
    body: LoginRequest, auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> LoginResponse:
    """認証を行い、アクセストークンを発行します。"""
    username, password = body.to_domain()
    token = auth_service.login(username, password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが正しくありません",
        )
    return LoginResponse.from_domain(token)


@router.get("/me")
async def me(
    username: Annotated[Username, Depends(get_authenticated_user)],
) -> MeResponse:
    """現在のログインユーザー情報を取得します。"""
    return MeResponse.from_domain(username)


@router.get("/users")
async def list_users(
    _: Annotated[Username, Depends(get_authenticated_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> list[str]:
    """システムに登録されているユーザー一覧を取得します。"""
    return [u.value for u in auth_service.get_all_usernames()]
