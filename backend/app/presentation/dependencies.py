"""FastAPI の依存性注入（DI）を組み立てる Composition Root。"""

from typing import Annotated

from fastapi import Depends, HTTPException, Query, WebSocket, WebSocketException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.interfaces.auth import TicketStore
from ..application.services.auth_service import AuthService
from ..application.services.connection_service import ConnectionService
from ..application.services.direct_request_service import DirectRequestService
from ..application.services.feed_query_service import FeedQueryService
from ..application.services.global_chat_service import GlobalChatService
from ..application.services.user_settings_service import UserSettingsService
from ..application.uow import UnitOfWork
from ..domain.entities.user import User
from ..domain.primitives.primitives import AuthToken
from ..infrastructure.auth.jwt_service import JwtServiceImpl
from ..infrastructure.auth.login_rate_limiter import LoginRateLimiter
from ..infrastructure.auth.password_hasher import PasswordHasher
from ..infrastructure.auth.redis_ticket_store import RedisTicketStore
from ..infrastructure.config import settings
from ..infrastructure.persistence.sa_message_repository import (
    SqlAlchemyMessageRepository,
)
from ..infrastructure.persistence.sa_outbox_repository import (
    SqlAlchemyDeliveryFeedRepository,
)
from ..infrastructure.persistence.sa_refresh_token_repository import (
    SqlAlchemyRefreshTokenRepository,
)
from ..infrastructure.persistence.sa_task_repository import (
    SqlAlchemyTaskRepository,
)
from ..infrastructure.persistence.sa_uow import SqlAlchemyUnitOfWork
from ..infrastructure.persistence.sa_user_repository import (
    SqlAlchemyUserRepository,
)
from ..infrastructure.persistence.sa_user_settings_repository import (
    SqlAlchemyUserSettingsRepository,
)
from ..infrastructure.persistence.session import get_db
from ..infrastructure.rate_limiter import FixedWindowRateLimiter
from .websockets.manager import ChatManager, get_manager

security = HTTPBearer()

# --- Repository / Publisher / UoW ---


def get_uow(db: Annotated[AsyncSession, Depends(get_db)]) -> UnitOfWork:
    """UnitOfWork の取得"""
    return SqlAlchemyUnitOfWork(
        db,
        SqlAlchemyTaskRepository(db),
        SqlAlchemyMessageRepository(db),
        SqlAlchemyDeliveryFeedRepository(db),
        SqlAlchemyUserSettingsRepository(db),
        SqlAlchemyUserRepository(db),
        SqlAlchemyRefreshTokenRepository(db),
    )


def get_chat_manager() -> ChatManager:
    """ChatManager シングルトンの取得"""
    return get_manager()


# --- Application Services ---


_ticket_store: TicketStore | None = None
_login_rate_limiter: LoginRateLimiter | None = None
_chat_message_rate_limiter: FixedWindowRateLimiter | None = None
_direct_request_rate_limiter: FixedWindowRateLimiter | None = None
_status_update_rate_limiter: FixedWindowRateLimiter | None = None


def get_login_rate_limiter() -> LoginRateLimiter:
    """LoginRateLimiter シングルトンの取得。"""
    global _login_rate_limiter
    if _login_rate_limiter is None:
        _login_rate_limiter = LoginRateLimiter(
            redis_url=settings.REDIS_URL,
            ip_max_attempts=settings.LOGIN_RATE_LIMIT_IP_MAX_ATTEMPTS,
            ip_window_seconds=settings.LOGIN_RATE_LIMIT_IP_WINDOW_SECONDS,
            user_max_attempts=settings.LOGIN_RATE_LIMIT_USER_MAX_ATTEMPTS,
            user_window_seconds=settings.LOGIN_RATE_LIMIT_USER_WINDOW_SECONDS,
        )
    return _login_rate_limiter


def get_chat_message_rate_limiter() -> FixedWindowRateLimiter:
    """グローバルチャットメッセージ送信用 FixedWindowRateLimiter シングルトンの取得。"""
    global _chat_message_rate_limiter
    if _chat_message_rate_limiter is None:
        _chat_message_rate_limiter = FixedWindowRateLimiter(
            redis_url=settings.REDIS_URL,
            key_prefix="rate_limit:chat_message:",
            max_attempts=settings.CHAT_MESSAGE_RATE_LIMIT_MAX_ATTEMPTS,
            window_seconds=settings.CHAT_MESSAGE_RATE_LIMIT_WINDOW_SECONDS,
        )
    return _chat_message_rate_limiter


def get_direct_request_rate_limiter() -> FixedWindowRateLimiter:
    """ダイレクトリクエスト送信用 FixedWindowRateLimiter シングルトンの取得。"""
    global _direct_request_rate_limiter
    if _direct_request_rate_limiter is None:
        _direct_request_rate_limiter = FixedWindowRateLimiter(
            redis_url=settings.REDIS_URL,
            key_prefix="rate_limit:direct_request:",
            max_attempts=settings.DIRECT_REQUEST_RATE_LIMIT_MAX_ATTEMPTS,
            window_seconds=settings.DIRECT_REQUEST_RATE_LIMIT_WINDOW_SECONDS,
        )
    return _direct_request_rate_limiter


def get_status_update_rate_limiter() -> FixedWindowRateLimiter:
    """ステータス更新用 FixedWindowRateLimiter シングルトンの取得。"""
    global _status_update_rate_limiter
    if _status_update_rate_limiter is None:
        _status_update_rate_limiter = FixedWindowRateLimiter(
            redis_url=settings.REDIS_URL,
            key_prefix="rate_limit:status_update:",
            max_attempts=settings.STATUS_UPDATE_RATE_LIMIT_MAX_ATTEMPTS,
            window_seconds=settings.STATUS_UPDATE_RATE_LIMIT_WINDOW_SECONDS,
        )
    return _status_update_rate_limiter


def get_ticket_store() -> TicketStore:
    """TicketStore の取得"""
    global _ticket_store
    if _ticket_store is None:
        _ticket_store = RedisTicketStore(settings.REDIS_URL)
    return _ticket_store


def get_auth_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> AuthService:
    """AuthService の取得"""
    return AuthService(
        uow,
        jwt=JwtServiceImpl(),
        password_verifier=PasswordHasher(),
        refresh_token_expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )


def get_global_chat_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> GlobalChatService:
    """GlobalChatService の取得"""
    return GlobalChatService(uow)


def get_direct_request_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> DirectRequestService:
    """DirectRequestService の取得"""
    return DirectRequestService(uow)


def get_connection_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> ConnectionService:
    """ConnectionService の取得"""
    return ConnectionService(uow)


def get_feed_query_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> FeedQueryService:
    """FeedQueryService の取得"""
    return FeedQueryService(uow)


def get_user_settings_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> UserSettingsService:
    """UserSettingsService の取得"""
    return UserSettingsService(uow)


# --- Authentication Dependencies ---


async def get_authenticated_user(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> User:
    """REST API 用の認証依存関係。User エンティティを返します。"""
    token = credentials.credentials
    user_id = auth_service.get_user_id_from_token(AuthToken(token))
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なトークンです",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザーが存在しません",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_ws_authenticated_user(
    websocket: WebSocket,
    ticket_store: Annotated[TicketStore, Depends(get_ticket_store)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    ticket: Annotated[str, Query(...)],
) -> User:
    """WebSocket 用の認証依存関係。チケット検証後に User エンティティを返します。"""
    # 1. Origin の検証
    origin = websocket.headers.get("origin", "")
    if origin != settings.ALLOWED_ORIGIN:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    # 2. チケットの検証
    user_id = await ticket_store.consume_ticket(ticket)
    if not user_id:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or expired ticket"
        )

    # 3. ユーザー情報の取得
    user = await auth_service.get_user_by_id(user_id)
    if not user:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, reason="User not found"
        )

    return user
