"""認証関連の REST API エンドポイント定義。"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ...application.interfaces.auth import TicketStore
from ...application.services.auth_service import AuthService
from ...domain.primitives.primitives import AuthToken, Password, RefreshToken, Username
from ..dependencies import get_auth_service, get_authenticated_user, get_ticket_store

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
    refresh_token: str
    token_type: str

    @classmethod
    def from_domain(cls, token_pair: tuple[AuthToken, RefreshToken]) -> "LoginResponse":
        """トークンペアからレスポンス DTO を生成します。"""
        access, refresh = token_pair
        return cls(
            access_token=access.value, refresh_token=refresh.value, token_type="bearer"
        )


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
    """認証を行い、アクセストークンとリフレッシュトークンを発行します。"""
    username, password = body.to_domain()
    token_pair = auth_service.login(username, password)
    if not token_pair:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが正しくありません",
        )
    return LoginResponse.from_domain(token_pair)


class RefreshRequest(BaseModel):
    """リフレッシュリクエスト用のスキーマ"""

    refresh_token: str


@router.post("/refresh")
async def refresh(
    body: RefreshRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> LoginResponse:
    """リフレッシュトークンを使って新しいトークンペアを発行します。"""
    token_pair = auth_service.refresh(RefreshToken(body.refresh_token))
    if not token_pair:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="リフレッシュトークンが無効または期限切れです",
        )
    return LoginResponse.from_domain(token_pair)


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


class WsTicketResponse(BaseModel):
    """WebSocket チケットレスポンス用のスキーマ"""

    ticket: str


@router.post("/ws-ticket")
async def ws_ticket(
    username: Annotated[Username, Depends(get_authenticated_user)],
    ticket_store: Annotated[TicketStore, Depends(get_ticket_store)],
) -> WsTicketResponse:
    """WebSocket 接続用のワンタイムチケットを発行します。"""
    ticket = await ticket_store.create_ticket(username)
    return WsTicketResponse(ticket=ticket)
