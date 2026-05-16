"""テスト全体で共有するフィクスチャ定義。"""

import re
from datetime import datetime, timezone
from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import make_url, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.domain.entities.message import Message
from app.domain.primitives.primitives import EntityId, MessageText, Username
from app.infrastructure.config import settings
from app.infrastructure.persistence.orm_models import Base
from app.infrastructure.persistence.sa_message_repository import (
    SqlAlchemyMessageRepository,
)
from app.infrastructure.persistence.sa_outbox_repository import (
    SqlAlchemyDeliveryFeedRepository,
)
from app.infrastructure.persistence.sa_task_repository import (
    SqlAlchemyTaskRepository,
)
from app.infrastructure.persistence.sa_uow import SqlAlchemyUnitOfWork


@pytest.fixture
def mock_uow():
    """DB 不要の UnitOfWork モック。async with / commit / rollback に対応。"""
    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.messages = AsyncMock()
    uow.tasks = AsyncMock()
    uow.outbox = AsyncMock()
    return uow


@pytest.fixture
def saved_message():
    """テスト用の永続化済み Message エンティティ。"""
    return Message(
        id=EntityId(1),
        username=Username("alice"),
        text=MessageText("hello"),
        created_at=datetime.now(timezone.utc),
    )


# --- Integration Test Fixtures ---


@pytest.fixture(scope="session")
def test_db_url() -> str:
    """テスト用データベースの URL を返します。"""
    return (
        make_url(settings.DATABASE_URL)
        .set(database="chat_db_test")
        .render_as_string(hide_password=False)
    )


@pytest.fixture(scope="session")
async def setup_test_db(test_db_url: str) -> AsyncGenerator[None, None]:
    """テスト用データベース自体の作成と破棄。"""
    # chat_db_test を作成するために、一時的に postgres DB に接続
    admin_url = (
        make_url(settings.DATABASE_URL)
        .set(database="postgres")
        .render_as_string(hide_password=False)
    )
    admin_engine = create_async_engine(
        admin_url, isolation_level="AUTOCOMMIT", poolclass=NullPool
    )

    db_name = make_url(test_db_url).database
    if not db_name or not re.fullmatch(r"[a-zA-Z0-9_-]+", db_name):
        raise ValueError(f"Invalid database name: {db_name}")

    async with admin_engine.connect() as conn:
        # 既存の DB があれば削除（クリーンな状態から開始）
        await conn.execute(
            text(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = :db_name AND pid <> pg_backend_pid()"
            ).bindparams(db_name=db_name)
        )
        await conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
        await conn.execute(text(f"CREATE DATABASE {db_name}"))

    yield

    async with admin_engine.connect() as conn:
        # テスト終了後に DB を削除（残存コネクションを強制切断してから削除）
        await conn.execute(
            text(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = :db_name AND pid <> pg_backend_pid()"
            ).bindparams(db_name=db_name)
        )
        await conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))

    await admin_engine.dispose()


@pytest.fixture(scope="session")
async def db_engine(
    setup_test_db: None, test_db_url: str
) -> AsyncGenerator[AsyncEngine, None]:
    """テスト用 DB エンジンを提供。テスト終了時に破棄。"""
    engine = create_async_engine(test_db_url, echo=False, poolclass=NullPool)

    # 初回に全テーブルを作成
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """テストごとの非同期セッションを提供。
    外部トランザクションを張り、内部の commit() を SAVEPOINT に降格させることで、
    テスト終了後に外部トランザクションをロールバックし DB をクリーンに保ちます。
    """
    async with db_engine.connect() as conn:
        await conn.begin()
        session_factory = async_sessionmaker(
            bind=conn,
            class_=AsyncSession,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        async with session_factory() as session:
            yield session
        await conn.rollback()


@pytest.fixture
async def db_uow(db_session: AsyncSession) -> SqlAlchemyUnitOfWork:
    """本物の DB セッションを使用した UnitOfWork を提供します。"""
    return SqlAlchemyUnitOfWork(
        db_session,
        SqlAlchemyTaskRepository(db_session),
        SqlAlchemyMessageRepository(db_session),
        SqlAlchemyDeliveryFeedRepository(db_session),
    )
