"""ダイレクトリクエスト REST API の結合テスト。"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.domain.entities.task import DraftTask
from app.domain.entities.user import User
from app.domain.primitives.primitives import (
    HashedPassword,
    TaskText,
    Userid,
    Username,
)
from app.domain.primitives.task_status import TaskStatus
from app.infrastructure.persistence.sa_task_repository import (
    SqlAlchemyTaskRepository,
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
async def test_get_direct_requests_recent(db_session, override_auth, seeded_users):
    """パラメータなしでアクセスした際、自分に関連する最新のダイレクトリクエストが取得できることを確認。"""
    repo = SqlAlchemyTaskRepository(db_session)
    alice_id = override_auth.id
    bob_id = seeded_users["bob"]

    for i in range(5):
        await repo.save(
            DraftTask(
                sender_id=alice_id,
                recipient_id=bob_id,
                sender=Username("alice"),
                recipient=Username("bob"),
                text=TaskText(f"req_{i}"),
                status=TaskStatus.REQUESTED,
            )
        )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/direct_requests",
            headers={"Authorization": "Bearer dummy_token"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        assert data[0]["text"] == "req_0"
        assert data[4]["text"] == "req_4"
        assert data[0]["is_history"] is True


@pytest.mark.anyio
async def test_get_direct_requests_before(db_session, override_auth, seeded_users):
    """before_id を指定した際、指定 ID より前の
    ダイレクトリクエストが取得できることを確認。
    """
    repo = SqlAlchemyTaskRepository(db_session)
    alice_id = override_auth.id
    bob_id = seeded_users["bob"]

    saved_tasks = []
    for i in range(5):
        task = await repo.save(
            DraftTask(
                sender_id=alice_id,
                recipient_id=bob_id,
                sender=Username("alice"),
                recipient=Username("bob"),
                text=TaskText(f"req_{i}"),
                status=TaskStatus.REQUESTED,
            )
        )
        saved_tasks.append(task)

    # 4番目（インデックス3, req_3）を基準にする
    target_id = saved_tasks[3].id.value

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"/api/direct_requests?before_id={target_id}&limit=2",
            headers={"Authorization": "Bearer dummy_token"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["text"] == "req_1"
        assert data[1]["text"] == "req_2"
        assert data[0]["is_history"] is True


@pytest.mark.anyio
async def test_get_direct_requests_after(db_session, override_auth, seeded_users):
    """after_id を指定した際、指定 ID より後の
    ダイレクトリクエストが取得できることを確認。
    """
    repo = SqlAlchemyTaskRepository(db_session)
    alice_id = override_auth.id
    bob_id = seeded_users["bob"]

    saved_tasks = []
    for i in range(5):
        task = await repo.save(
            DraftTask(
                sender_id=alice_id,
                recipient_id=bob_id,
                sender=Username("alice"),
                recipient=Username("bob"),
                text=TaskText(f"req_{i}"),
                status=TaskStatus.REQUESTED,
            )
        )
        saved_tasks.append(task)

    # 2番目（インデックス1, req_1）を基準にする
    target_id = saved_tasks[1].id.value

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"/api/direct_requests?after_id={target_id}",
            headers={"Authorization": "Bearer dummy_token"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["text"] == "req_2"
        assert data[1]["text"] == "req_3"
        assert data[2]["text"] == "req_4"
        assert data[0]["is_history"] is True
