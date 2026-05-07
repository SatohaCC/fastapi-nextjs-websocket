"""DB 接続とテーブル生成のスモークテスト。"""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_db_connection(db_session: AsyncSession):
    """DB 接続と基本的なクエリの実行を確認するスモークテスト。"""
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


@pytest.mark.asyncio
async def test_tables_created(db_session: AsyncSession):
    """Base.metadata.create_all によりテーブルが作成されていることを確認。"""
    # messages テーブルが存在するか確認
    stmt = (
        "SELECT EXISTS ("
        "SELECT FROM information_schema.tables WHERE table_name = 'messages')"
    )
    result = await db_session.execute(text(stmt))
    assert result.scalar() is True
