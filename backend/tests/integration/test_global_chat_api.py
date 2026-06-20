"""グローバルチャット REST API の結合テスト。"""

from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from app.domain.entities.message import DraftMessage
from app.domain.entities.user import User
from app.domain.primitives.primitives import (
    HashedPassword,
    MessageText,
    Userid,
    Username,
)
from app.infrastructure.persistence.sa_message_repository import (
    SqlAlchemyMessageRepository,
)
from app.infrastructure.persistence.session import get_db
from app.main import app
from app.presentation.dependencies import get_authenticated_user


@pytest.fixture(autouse=True)
def override_db(db_session):
    """FastAPI の DB 依存関係をテスト用のセッションにオーバーライドします。"""
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def override_auth(seeded_users):
    """認証の依存関係をシードされた alice にオーバーライドします。"""
    alice_id = seeded_users["alice"]
    test_user = User(
        id=alice_id,
        userid=Userid("alice"),
        username=Username("alice"),
        hashed_password=HashedPassword("$2b$dummy_hash"),
    )
    app.dependency_overrides[get_authenticated_user] = lambda: test_user
    yield test_user
    app.dependency_overrides.pop(get_authenticated_user, None)


@pytest.mark.anyio
async def test_get_messages_recent(db_session, override_auth):
    """パラメータなしでアクセスした際、最新のメッセージが取得できることを確認。"""
    repo = SqlAlchemyMessageRepository(db_session)
    user_id = override_auth.id

    for i in range(5):
        await repo.save(
            DraftMessage(
                user_id=user_id,
                username=Username("alice"),
                text=MessageText(f"msg_{i}"),
                created_at=datetime.now(timezone.utc),
            )
        )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/global_chat/messages",
            headers={"Authorization": "Bearer dummy_token"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        assert data[0]["text"] == "msg_0"
        assert data[4]["text"] == "msg_4"
        assert data[0]["is_history"] is True


@pytest.mark.anyio
async def test_get_messages_before(db_session, override_auth):
    """before_id を指定した際、指定 ID より前のメッセージが
    古い順に取得できることを確認。
    """
    repo = SqlAlchemyMessageRepository(db_session)
    user_id = override_auth.id

    saved_messages = []
    for i in range(5):
        msg = await repo.save(
            DraftMessage(
                user_id=user_id,
                username=Username("alice"),
                text=MessageText(f"msg_{i}"),
                created_at=datetime.now(timezone.utc),
            )
        )
        saved_messages.append(msg)

    # 4番目（インデックス3, msg_3）を基準にする
    target_id = saved_messages[3].id.value

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"/api/global_chat/messages?before_id={target_id}&limit=2",
            headers={"Authorization": "Bearer dummy_token"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["text"] == "msg_1"
        assert data[1]["text"] == "msg_2"
        assert data[0]["is_history"] is True


@pytest.mark.anyio
async def test_get_messages_after(db_session, override_auth):
    """after_id を指定した際、指定 ID より後のメッセージが
    古い順に取得できることを確認。
    """
    repo = SqlAlchemyMessageRepository(db_session)
    user_id = override_auth.id

    saved_messages = []
    for i in range(5):
        msg = await repo.save(
            DraftMessage(
                user_id=user_id,
                username=Username("alice"),
                text=MessageText(f"msg_{i}"),
                created_at=datetime.now(timezone.utc),
            )
        )
        saved_messages.append(msg)

    # 2番目（インデックス1, msg_1）を基準にする
    target_id = saved_messages[1].id.value

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"/api/global_chat/messages?after_id={target_id}",
            headers={"Authorization": "Bearer dummy_token"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["text"] == "msg_2"
        assert data[1]["text"] == "msg_3"
        assert data[2]["text"] == "msg_4"
        assert data[0]["is_history"] is True
