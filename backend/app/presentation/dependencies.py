"""FastAPI の依存性注入（DI）を組み立てる Composition Root。"""

from typing import Annotated

from fastapi import Depends, HTTPException, Query, WebSocket, WebSocketException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.services.auth_service import AuthService
from ..application.services.chat_service import ChatService
from ..application.services.connection_service import ConnectionService
from ..application.services.feed_query_service import FeedQueryService
from ..application.services.request_service import RequestService
from ..application.uow import UnitOfWork
from ..infrastructure.auth.jwt_service import JwtServiceImpl
from ..infrastructure.config import settings
from ..infrastructure.messaging.redis_publisher import event_publisher
from ..infrastructure.persistence.sa_message_repository import (
    SqlAlchemyMessageRepository,
)
from ..infrastructure.persistence.sa_outbox_repository import (
    SqlAlchemyDeliveryFeedRepository,
)
from ..infrastructure.persistence.sa_request_repository import (
    SqlAlchemyRequestRepository,
)
from ..infrastructure.persistence.sa_uow import SqlAlchemyUnitOfWork
from ..infrastructure.persistence.session import get_db
from .websockets.manager import ChatManager, get_manager

security = HTTPBearer()

# --- Repository / Publisher / UoW ---


def get_uow(db: Annotated[AsyncSession, Depends(get_db)]) -> UnitOfWork:
    """UnitOfWork の取得"""
    return SqlAlchemyUnitOfWork(
        db,
        SqlAlchemyRequestRepository(db),
        SqlAlchemyMessageRepository(db),
        SqlAlchemyDeliveryFeedRepository(db),
    )


def get_chat_manager() -> ChatManager:
    """ChatManager シングルトンの取得"""
    return get_manager()


# --- Application Services ---


def get_auth_service() -> AuthService:
    """AuthService の取得"""
    return AuthService(jwt=JwtServiceImpl(), users=settings.USERS)


def get_chat_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> ChatService:
    """ChatService の取得"""
    return ChatService(uow)


def get_request_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> RequestService:
    """RequestService の取得"""
    return RequestService(uow)


def get_connection_service() -> ConnectionService:
    """ConnectionService の取得"""
    return ConnectionService(event_publisher.publish)


def get_feed_query_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> FeedQueryService:
    """FeedQueryService の取得"""
    return FeedQueryService(uow)


# --- Authentication Dependencies ---


async def get_authenticated_user(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> str:
    """REST API 用の認証依存関係"""
    token = credentials.credentials
    username = auth_service.get_user_from_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なトークンです",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username


async def get_ws_authenticated_user(
    websocket: WebSocket,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    token: str = Query(...),
) -> str:
    """WebSocket 用の認証依存関係"""
    # 1. Origin の検証
    origin = websocket.headers.get("origin", "")
    if origin != settings.ALLOWED_ORIGIN:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    # 2. トークンの検証
    username = auth_service.get_user_from_token(token)
    if not username:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or expired token"
        )

    return username
