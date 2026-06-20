"""認証関連の REST API エンドポイント定義。"""

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from ...application.interfaces.auth import TicketStore
from ...application.services.auth_service import AuthService
from ...domain.entities.refresh_token import RefreshToken as RefreshTokenEntity
from ...domain.entities.user import User
from ...domain.exceptions import DomainValidationError
from ...domain.primitives.primitives import (
    AuthToken,
    IpAddress,
    Password,
    RefreshToken,
    SessionId,
    UserAgent,
    Userid,
    Username,
)
from ...infrastructure.auth.login_rate_limiter import LoginRateLimiter
from ..dependencies import (
    get_access_token,
    get_auth_service,
    get_authenticated_user,
    get_login_rate_limiter,
    get_ticket_store,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    """ログインリクエスト用のスキーマ"""

    userid: str
    password: str

    def to_domain(self) -> tuple[Userid, Password]:
        """フィールドをドメインプリミティブへ変換します。"""
        return Userid(self.userid), Password(self.password)


class RegisterRequest(BaseModel):
    """新規登録リクエスト用のスキーマ"""

    userid: str
    username: str
    password: str

    def to_domain(self) -> tuple[Userid, Username, Password]:
        """フィールドをドメインプリミティブへ変換します。"""
        return (
            Userid(self.userid),
            Username(self.username),
            Password(self.password),
        )


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

    id: str
    userid: str
    username: str

    @classmethod
    def from_domain(cls, user: User) -> "MeResponse":
        """User エンティティからレスポンス DTO を生成します。"""
        return cls(
            id=str(user.id.value),
            userid=user.userid.value,
            username=user.username.value,
        )


class ChangePasswordRequest(BaseModel):
    """パスワード変更リクエスト用のスキーマ"""

    current_password: str
    new_password: str

    def to_domain(self) -> tuple[Password, Password]:
        """リクエストデータをドメイン値オブジェクトに変換します。"""
        return Password(self.current_password), Password(self.new_password)


class UpdateUsernameRequest(BaseModel):
    """表示名変更リクエスト用のスキーマ"""

    username: str

    def to_domain(self) -> Username:
        """リクエストデータをドメイン値オブジェクトに変換します。"""
        return Username(self.username)


class ForgotPasswordRequest(BaseModel):
    """パスワードリセット要求リクエスト用のスキーマ"""

    userid: str

    def to_domain(self) -> Userid:
        """リクエストデータをドメイン値オブジェクトに変換します。"""
        return Userid(self.userid)


class ResetPasswordRequest(BaseModel):
    """パスワードリセット実行リクエスト用のスキーマ"""

    token: str
    new_password: str

    def to_domain(self) -> Password:
        """リクエストデータをドメイン値オブジェクトに変換します。"""
        return Password(self.new_password)


@router.post("/token")
async def login(
    request: Request,
    body: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    rate_limiter: Annotated[LoginRateLimiter, Depends(get_login_rate_limiter)],
) -> LoginResponse:
    """認証を行い、アクセストークンとリフレッシュトークンを発行します。"""
    ip_str = request.client.host if request.client else None
    if await rate_limiter.is_limited(ip_str, body.userid):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="ログイン試行回数が上限に達しました。しばらく待ってから再試行してください。",
        )
    userid, password = body.to_domain()
    ua_str = request.headers.get("user-agent")
    ip = IpAddress(ip_str) if ip_str else None
    ua = UserAgent(ua_str) if ua_str else None
    token_pair = await auth_service.login(
        userid, password, ip_address=ip, user_agent=ua
    )
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
    request: Request,
    body: RefreshRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> LoginResponse:
    """リフレッシュトークンを使って新しいトークンペアを発行します。"""
    ip_str = request.client.host if request.client else None
    ua_str = request.headers.get("user-agent")
    ip = IpAddress(ip_str) if ip_str else None
    ua = UserAgent(ua_str) if ua_str else None
    token_pair = await auth_service.refresh(
        RefreshToken(body.refresh_token), ip_address=ip, user_agent=ua
    )
    if not token_pair:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="リフレッシュトークンが無効または期限切れです",
        )
    return LoginResponse.from_domain(token_pair)


class LogoutRequest(BaseModel):
    """ログアウトリクエスト用のスキーマ"""

    refresh_token: str


@router.post("/logout")
async def logout(
    body: LogoutRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """リフレッシュトークンを無効化（DBから物理削除）し、ログアウト処理を行います。"""
    await auth_service.logout(RefreshToken(body.refresh_token))
    return {"success": True}


@router.get("/me")
async def me(
    user: Annotated[User, Depends(get_authenticated_user)],
) -> MeResponse:
    """現在のログインユーザー情報を取得します。"""
    return MeResponse.from_domain(user)


class UserListResponse(BaseModel):
    """システムに登録されているユーザー一覧のアイテム用のスキーマ。"""

    id: str
    username: str


@router.get("/users", response_model=list[UserListResponse])
async def list_users(
    _: Annotated[User, Depends(get_authenticated_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> list[UserListResponse]:
    """システムに登録されているユーザー一覧を取得します。"""
    users = await auth_service.get_all_users()
    return [
        UserListResponse(id=str(u.id.value), username=u.username.value) for u in users
    ]


class WsTicketResponse(BaseModel):
    """WebSocket チケットレスポンス用のスキーマ"""

    ticket: str


@router.post("/ws-ticket")
async def ws_ticket(
    user: Annotated[User, Depends(get_authenticated_user)],
    token: Annotated[AuthToken, Depends(get_access_token)],
    ticket_store: Annotated[TicketStore, Depends(get_ticket_store)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> WsTicketResponse:
    """WebSocket 接続用のワンタイムチケットを発行します。"""
    if not await auth_service.is_session_valid(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="セッションが無効または削除されています",
            headers={"WWW-Authenticate": "Bearer"},
        )
    session_id = auth_service.get_session_id_from_token(token)
    ticket = await ticket_store.create_ticket(user.id, session_id)
    return WsTicketResponse(ticket=ticket)


class ActiveSessionResponse(BaseModel):
    """アクティブなセッション情報のレスポンススキーマ"""

    id: str
    created_at: datetime
    expires_at: datetime
    ip_address: str | None
    user_agent: str | None
    token_hash: str

    @classmethod
    def from_domain(cls, token: RefreshTokenEntity) -> "ActiveSessionResponse":
        """ドメインエンティティからレスポンス DTO を生成します。"""
        return cls(
            id=str(token.id),
            created_at=token.created_at,
            expires_at=token.expires_at,
            ip_address=token.ip_address.value if token.ip_address else None,
            user_agent=token.user_agent.value if token.user_agent else None,
            token_hash=token.token_hash.value,
        )


@router.get("/sessions", response_model=list[ActiveSessionResponse])
async def list_sessions(
    user: Annotated[User, Depends(get_authenticated_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> list[ActiveSessionResponse]:
    """現在のログインユーザーのアクティブセッション一覧を取得します。"""
    sessions = await auth_service.get_active_sessions(user.id)
    return [ActiveSessionResponse.from_domain(s) for s in sessions]


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: uuid.UUID,
    user: Annotated[User, Depends(get_authenticated_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """指定されたセッションを無効化（削除）します。"""
    success = await auth_service.revoke_session(user.id, SessionId(session_id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定されたセッションが見つからないか、所有権がありません",
        )
    return {"success": True}


@router.post(
    "/register", response_model=MeResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    body: RegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> MeResponse:
    """新規ユーザー登録を行い、作成されたユーザー情報を返します。"""
    userid, username, password = body.to_domain()
    try:
        user = await auth_service.register(userid, username, password)
        return MeResponse.from_domain(user)
    except DomainValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/me")
async def delete_account(
    user: Annotated[User, Depends(get_authenticated_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """現在のログインユーザーのアカウントを削除します。"""
    success = await auth_service.delete_account(user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )
    return {"success": True}


@router.post("/change-password")
async def change_password(
    body: ChangePasswordRequest,
    user: Annotated[User, Depends(get_authenticated_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """現在のログインユーザーのパスワードを変更します。"""
    current_pwd, new_pwd = body.to_domain()
    try:
        await auth_service.change_password(user.id, current_pwd, new_pwd)
        return {"success": True}
    except DomainValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch("/me", response_model=MeResponse)
async def update_username(
    body: UpdateUsernameRequest,
    user: Annotated[User, Depends(get_authenticated_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> MeResponse:
    """現在のユーザーの表示名（username）を変更します。"""
    new_username = body.to_domain()
    try:
        updated_user = await auth_service.update_username(user.id, new_username)
        return MeResponse.from_domain(updated_user)
    except DomainValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/forgot-password")
async def forgot_password(
    body: ForgotPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """パスワードリセット用リンクの発行を要求します（メール送信シミュレーション）。"""
    userid = body.to_domain()
    await auth_service.forgot_password(userid)
    return {"success": True}


@router.post("/reset-password")
async def reset_password(
    body: ResetPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """パスワードリセット用トークンを検証し、パスワードをリセットします。"""
    new_pwd = body.to_domain()
    try:
        await auth_service.reset_password(body.token, new_pwd)
        return {"success": True}
    except DomainValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
