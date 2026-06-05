"""SqlAlchemyUserRepository の統合テスト。"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.primitives.primitives import Username
from app.infrastructure.persistence.sa_user_repository import (
    SqlAlchemyUserRepository,
)


@pytest.mark.asyncio
async def test_get_by_username_returns_none_if_not_found(db_session: AsyncSession):
    """存在しないユーザーを取得しようとした場合に None が返ることを確認します。"""
    repo = SqlAlchemyUserRepository(db_session)
    user = await repo.get_by_username(Username("nonexistent"))
    assert user is None


@pytest.mark.asyncio
async def test_save_and_get_user(db_session: AsyncSession):
    """ユーザー情報を保存し、取得できることを確認します。"""
    repo = SqlAlchemyUserRepository(db_session)
    username = Username("dave")
    hashed_password = "hashed_dave_password_123"

    user = User(username=username, hashed_password=hashed_password)

    # 保存
    saved = await repo.save(user)
    assert saved.username == username
    assert saved.hashed_password == hashed_password

    # 取得
    retrieved = await repo.get_by_username(username)
    assert retrieved is not None
    assert retrieved.username == username
    assert retrieved.hashed_password == hashed_password


@pytest.mark.asyncio
async def test_get_all_returns_all_users(db_session: AsyncSession):
    """登録されているすべてのユーザーを取得できることを確認します。"""
    repo = SqlAlchemyUserRepository(db_session)

    # 既存のユーザー数を取得（conftest でシードされている分）
    initial_users = await repo.get_all()
    initial_count = len(initial_users)

    # 新規ユーザー追加
    await repo.save(
        User(username=Username("eve"), hashed_password="hashed_eve_password")
    )
    await repo.save(
        User(username=Username("frank"), hashed_password="hashed_frank_password")
    )

    all_users = await repo.get_all()
    assert len(all_users) == initial_count + 2
    usernames = [u.username.value for u in all_users]
    assert "eve" in usernames
    assert "frank" in usernames
