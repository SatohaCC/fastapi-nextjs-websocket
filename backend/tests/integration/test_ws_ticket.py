"""WebSocket チケット発行の統合テスト。"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from app.domain.entities.refresh_token import RefreshToken as RefreshTokenEntity
from app.domain.primitives.primitives import SessionId, UserId
from app.infrastructure.auth.jwt_service import JwtServiceImpl
from app.infrastructure.persistence.session import get_db
from app.main import app
from app.presentation.dependencies import get_ticket_store


class FakeTicketStore:
    """テスト用のインメモリ TicketStore"""

    def __init__(self) -> None:
        """インメモリのチケット辞書を初期化します。"""
        self._tickets: dict[str, tuple[UserId, SessionId | None]] = {}

    async def create_ticket(
        self, user_id: UserId, session_id: SessionId | None = None
    ) -> str:
        """指定されたユーザー ID（とセッション ID）に対する
        接続チケットを生成・保存します。
        """
        ticket = f"ws_ticket_dummy_{uuid.uuid4()}"
        self._tickets[ticket] = (user_id, session_id)
        return ticket

    async def consume_ticket(
        self, ticket: str
    ) -> tuple[UserId, SessionId | None] | None:
        """チケットを検証し、有効な場合は
        (ユーザー ID, セッション ID) を返してチケットを削除します。
        """
        return self._tickets.pop(ticket, None)


@pytest.fixture(autouse=True)
def override_dependencies(db_session):
    """FastAPI の依存関係をテスト用にオーバーライドします。"""
    fake_ticket_store = FakeTicketStore()
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_ticket_store] = lambda: fake_ticket_store
    yield
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_ticket_store, None)


@pytest.mark.anyio
async def test_ws_ticket_session_validation(db_session, seeded_users):
    """セッションの有効・無効（削除済み）に応じて
    ws-ticket 発行が正しく認可・拒否されることを検証します。
    """
    alice_id = seeded_users["alice"]

    # JWT トークンペアの作成
    jwt_service = JwtServiceImpl()
    session_id = uuid.uuid7()
    access_token, refresh_token = jwt_service.create_token(alice_id, session_id)

    # 1. DBにセッション（リフレッシュトークン）が存在しない状態で ws-ticket を叩く
    # アクセストークン自体が有効であれば通す。
    # だが ws-ticket 内の is_session_valid で拒否される。)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # まずは認証に失敗することを確認（セッションレコードが存在しない）
        response = await client.post(
            "/api/auth/ws-ticket",
            headers={"Authorization": f"Bearer {access_token.value}"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "セッションが無効または削除されています"

    # 2. DBにセッションを保存する
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=7)
    db_token = RefreshTokenEntity.create(
        id=SessionId(session_id),
        user_id=alice_id,
        token_value=refresh_token.value,
        expires_at=expires_at,
        created_at=now,
    )
    # DBに直接インサート
    from app.infrastructure.persistence.sa_refresh_token_repository import (
        SqlAlchemyRefreshTokenRepository,
    )

    repo = SqlAlchemyRefreshTokenRepository(db_session)
    await repo.save(db_token)
    await db_session.commit()

    # 3. 再度 ws-ticket を叩く（今度はセッションがあるので成功するはず）
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/auth/ws-ticket",
            headers={"Authorization": f"Bearer {access_token.value}"},
        )
        assert response.status_code == 200
        assert "ticket" in response.json()

    # 4. セッションを削除する
    # ログアウトや管理者によるセッション無効化のシミュレーション
    await repo.delete_by_id(SessionId(session_id))
    await db_session.commit()

    # 5. セッション削除後に ws-ticket を叩く（拒否されるはず）
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/auth/ws-ticket",
            headers={"Authorization": f"Bearer {access_token.value}"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "セッションが無効または削除されています"
