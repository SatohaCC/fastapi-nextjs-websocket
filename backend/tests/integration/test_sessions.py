"""アクティブセッション一覧APIの統合テスト。"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from app.domain.entities.refresh_token import RefreshToken as RefreshTokenEntity
from app.domain.primitives.primitives import SessionId
from app.infrastructure.auth.jwt_service import JwtServiceImpl
from app.infrastructure.persistence.sa_refresh_token_repository import (
    SqlAlchemyRefreshTokenRepository,
)
from app.infrastructure.persistence.session import get_db
from app.main import app


@pytest.fixture(autouse=True)
def override_dependencies(db_session):
    """FastAPI の依存関係をテスト用にオーバーライドします。"""
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.anyio
async def test_list_sessions_marks_only_calling_session_as_current(
    db_session, seeded_users
):
    """複数セッションが存在する場合、呼び出しに使ったアクセストークンに
    対応するセッションのみ is_current が true になり、
    token_hash がレスポンスに含まれないことを検証します。
    """
    alice_id = seeded_users["alice"]
    jwt_service = JwtServiceImpl()
    repo = SqlAlchemyRefreshTokenRepository(db_session)

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=7)

    # セッション1（このアクセストークンで呼び出す）
    session_id_1 = uuid.uuid7()
    access_token_1, refresh_token_1 = jwt_service.create_token(alice_id, session_id_1)
    await repo.save(
        RefreshTokenEntity.create(
            id=SessionId(session_id_1),
            user_id=alice_id,
            token_value=refresh_token_1.value,
            expires_at=expires_at,
            created_at=now,
        )
    )

    # セッション2（別デバイスのセッション想定）
    session_id_2 = uuid.uuid7()
    _, refresh_token_2 = jwt_service.create_token(alice_id, session_id_2)
    await repo.save(
        RefreshTokenEntity.create(
            id=SessionId(session_id_2),
            user_id=alice_id,
            token_value=refresh_token_2.value,
            expires_at=expires_at,
            created_at=now,
        )
    )
    await db_session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/auth/sessions",
            headers={"Authorization": f"Bearer {access_token_1.value}"},
        )

    assert response.status_code == 200
    sessions = response.json()
    assert len(sessions) == 2

    for session in sessions:
        assert "token_hash" not in session

    current_sessions = [s for s in sessions if s["is_current"]]
    assert len(current_sessions) == 1
    assert current_sessions[0]["id"] == str(session_id_1)
