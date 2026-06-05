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
from ..domain.primitives.primitives import AuthToken, Username
from ..infrastructure.auth.jwt_service import JwtServiceImpl
from ..infrastructure.auth.redis_ticket_store import RedisTicketStore
from ..infrastructure.config import settings
from ..infrastructure.persistence.sa_message_repository import (
    SqlAlchemyMessageRepository,
)
from ..infrastructure.persistence.sa_outbox_repository import (
    SqlAlchemyDeliveryFeedRepository,
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
    )


def get_chat_manager() -> ChatManager:
    """ChatManager シングルトンの取得"""
    return get_manager()


# --- Application Services ---


_ticket_store: TicketStore | None = None


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
    return AuthService(uow, jwt=JwtServiceImpl())


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
) -> Username:
    """REST API 用の認証依存関係"""
    token = credentials.credentials
    username = auth_service.get_user_from_token(AuthToken(token))
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なトークンです",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username


async def get_ws_authenticated_user(
    websocket: WebSocket,
    ticket_store: Annotated[TicketStore, Depends(get_ticket_store)],
    ticket: Annotated[str, Query(...)],
) -> Username:
    """WebSocket 用の認証依存関係。ワンタイム・チケットの検証を行います。"""
    # 1. Origin の検証
    origin = websocket.headers.get("origin", "")
    if origin != settings.ALLOWED_ORIGIN:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    # 2. チケットの検証
    username = await ticket_store.consume_ticket(ticket)
    if not username:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or expired ticket"
        )

    return username
