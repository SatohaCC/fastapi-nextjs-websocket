"""SqlAlchemyUserRepository の統合テスト。"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.primitives.primitives import (
    HashedPassword,
    UserId,
    Userid,
    Username,
)
from app.infrastructure.persistence.sa_user_repository import (
    SqlAlchemyUserRepository,
)


@pytest.mark.asyncio
async def test_get_by_id_returns_none_if_not_found(db_session: AsyncSession):
    """存在しない ID を取得しようとした場合に None が返ることを確認します。"""
    repo = SqlAlchemyUserRepository(db_session)
    user = await repo.get_by_id(UserId(uuid.uuid7()))
    assert user is None


@pytest.mark.asyncio
async def test_get_by_userid_returns_none_if_not_found(db_session: AsyncSession):
    """存在しないユーザーIDを取得しようとした場合に None が返ることを確認します。"""
    repo = SqlAlchemyUserRepository(db_session)
    user = await repo.get_by_userid(Userid("nonexistent"))
    assert user is None


@pytest.mark.asyncio
async def test_save_and_get_user(db_session: AsyncSession):
    """ユーザー情報を保存し、ID およびログインIDで取得できることを確認します。"""
    repo = SqlAlchemyUserRepository(db_session)
    user_id = UserId(uuid.uuid7())
    userid = Userid("dave")
    username = Username("Dave Name")
    hashed_password = "$2b$hashed_dave_password_123"

    user = User(
        id=user_id,
        userid=userid,
        username=username,
        hashed_password=HashedPassword(hashed_password),
    )

    # 保存
    saved = await repo.save(user)
    assert saved.id == user_id
    assert saved.userid == userid
    assert saved.username == username
    assert saved.hashed_password.value == hashed_password

    # IDで取得
    retrieved_by_id = await repo.get_by_id(user_id)
    assert retrieved_by_id is not None
    assert retrieved_by_id.id == user_id
    assert retrieved_by_id.userid == userid
    assert retrieved_by_id.username == username
    assert retrieved_by_id.hashed_password.value == hashed_password

    # ログインIDで取得
    retrieved_by_name = await repo.get_by_userid(userid)
    assert retrieved_by_name is not None
    assert retrieved_by_name.id == user_id
    assert retrieved_by_name.userid == userid
    assert retrieved_by_name.username == username
    assert retrieved_by_name.hashed_password.value == hashed_password


@pytest.mark.asyncio
async def test_get_all_returns_all_users(db_session: AsyncSession):
    """登録されているすべてのユーザーを取得できることを確認します。"""
    repo = SqlAlchemyUserRepository(db_session)

    # 既存のユーザー数を取得（conftest でシードされている分）
    initial_users = await repo.get_all()
    initial_count = len(initial_users)

    # 新規ユーザー追加
    await repo.save(
        User(
            id=UserId(uuid.uuid7()),
            userid=Userid("eve"),
            username=Username("eve"),
            hashed_password=HashedPassword("$2b$hashed_eve_password"),
        )
    )
    await repo.save(
        User(
            id=UserId(uuid.uuid7()),
            userid=Userid("frank"),
            username=Username("frank"),
            hashed_password=HashedPassword("$2b$hashed_frank_password"),
        )
    )

    all_users = await repo.get_all()
    assert len(all_users) == initial_count + 2
    userids = [u.userid.value for u in all_users]
    assert "eve" in userids
    assert "frank" in userids
