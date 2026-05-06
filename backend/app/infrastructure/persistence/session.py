"""SQLAlchemy 非同期データベースセッションの設定と提供。"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..config import settings

# 非同期 DB エンジンの作成
engine = create_async_engine(settings.DATABASE_URL, echo=False)

# 非同期セッションファクトリの作成
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """FastAPI の依存関係として使用するためのデータベースセッションジェネレータ。
    各リクエストごとに新しいセッションを作成し、処理終了後に自動でクローズします。
    """
    async with AsyncSessionLocal() as session:
        yield session
