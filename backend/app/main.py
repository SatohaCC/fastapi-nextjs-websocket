"""FastAPI アプリケーションのエントリーポイント。"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from .domain.exceptions import (
    DomainException,
    DomainValidationError,
    EntityNotFoundException,
    InvalidOperationException,
    UnauthorizedException,
)
from .infrastructure.config import settings
from .infrastructure.messaging.redis_subscriber import redis_subscriber
from .infrastructure.messaging.relay_worker import relay_worker
from .infrastructure.persistence.orm_models import Base
from .infrastructure.persistence.session import AsyncSessionLocal, engine
from .presentation.api.auth import router as auth_router
from .presentation.api.feeds import router as feeds_router
from .presentation.api.messages import router as messages_router
from .presentation.api.requests import router as requests_router
from .presentation.websockets.endpoint import router as ws_router
from .presentation.websockets.manager import get_manager


@asynccontextmanager
async def lifespan(_: FastAPI):
    """アプリケーションのライフサイクル管理。"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # delivery_sequences 初期レコード（冪等）
        await conn.execute(
            text(
                "INSERT INTO delivery_sequences(name, last_id) VALUES('chat_global', 0), ('requests_global', 0) "
                "ON CONFLICT (name) DO NOTHING"
            )
        )
    print("Database tables initialized.")

    # DI 経由ではなく、ライフサイクル管理の文脈でシングルトンを取得
    manager = get_manager()
    redis_sub_task = asyncio.create_task(redis_subscriber(manager))
    relay_task = asyncio.create_task(
        relay_worker(AsyncSessionLocal, settings.REDIS_URL)
    )
    yield
    relay_task.cancel()
    redis_sub_task.cancel()
    try:
        await asyncio.gather(redis_sub_task, relay_task, return_exceptions=True)
    except asyncio.CancelledError:
        pass
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(EntityNotFoundException)
async def entity_not_found_handler(request: Request, exc: EntityNotFoundException):
    """エンティティが見つからない場合の例外ハンドラ。"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(UnauthorizedException)
async def unauthorized_handler(request: Request, exc: UnauthorizedException):
    """権限不足の場合の例外ハンドラ。"""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": str(exc)},
    )


@app.exception_handler(InvalidOperationException)
async def invalid_operation_handler(request: Request, exc: InvalidOperationException):
    """不正な操作が行われた場合の例外ハンドラ。"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


@app.exception_handler(DomainValidationError)
async def domain_validation_handler(request: Request, exc: DomainValidationError):
    """ドメインバリデーションエラーの場合の例外ハンドラ。"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)},
    )


@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    """一般的なドメインエラーの場合の例外ハンドラ。"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Domain error occurred", "message": str(exc)},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ALLOWED_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(feeds_router)
app.include_router(messages_router)
app.include_router(requests_router)
app.include_router(ws_router)
