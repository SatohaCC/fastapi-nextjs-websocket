"""SqlAlchemyUserSettingsRepository の統合テスト。"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user_settings import UserSettings
from app.domain.primitives.primitives import Username
from app.infrastructure.persistence.sa_user_settings_repository import (
    SqlAlchemyUserSettingsRepository,
)


@pytest.mark.asyncio
async def test_get_non_existent_settings(db_session: AsyncSession):
    """設定が存在しない場合は None を返すことを確認します。"""
    repo = SqlAlchemyUserSettingsRepository(db_session)
    settings = await repo.get(Username("non_existent"))
    assert settings is None


@pytest.mark.asyncio
async def test_upsert_and_get_settings(db_session: AsyncSession):
    """設定の保存と取得ができることを確認します。"""
    repo = SqlAlchemyUserSettingsRepository(db_session)
    username = Username("alice")
    settings = UserSettings(
        username=username,
        global_chat=False,
        direct_request=True,
        direct_request_updated=False,
    )

    # 保存（挿入）
    saved = await repo.upsert(settings)
    assert saved.username == username
    assert saved.global_chat is False
    assert saved.direct_request is True
    assert saved.direct_request_updated is False

    # 取得して検証
    retrieved = await repo.get(username)
    assert retrieved is not None
    assert retrieved.username == username
    assert retrieved.global_chat is False
    assert retrieved.direct_request is True
    assert retrieved.direct_request_updated is False

    # 更新（Upsert の Conflict 動作検証）
    updated_settings = UserSettings(
        username=username,
        global_chat=True,
        direct_request=False,
        direct_request_updated=True,
    )
    await repo.upsert(updated_settings)

    # 再度取得して検証
    retrieved2 = await repo.get(username)
    assert retrieved2 is not None
    assert retrieved2.global_chat is True
    assert retrieved2.direct_request is False
    assert retrieved2.direct_request_updated is True
