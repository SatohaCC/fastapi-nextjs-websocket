"""アプリケーション全体の設定を管理するモジュール。"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーション全体の設定を管理するクラス。
    環境変数によって各項目を上書きすることが可能です。
    """

    # CORS 設定
    ALLOWED_ORIGIN: str = "http://localhost:3000"

    # WebSocket ハートビート設定
    PING_INTERVAL: int = 10
    PONG_TIMEOUT: int = 5

    # データベース設定 (SQLAlchemy + asyncpg)
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/chat_db"

    # Redis 設定 (Pub/Sub 用)
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CHANNEL: str = "chat"
    REDIS_SEQ_KEY: str = "chat:seq"

    # JWT 認証設定
    SECRET_KEY: str = "dev-secret-key-do-not-use-in-production"
    ALGORITHM: str = "HS256"
    TOKEN_EXPIRE_MINUTES: int = 30

    # 簡易ユーザーマスター（デモ用）
    # key: username, value: password
    USERS: dict[str, str] = {
        "alice": "password1",
        "bob": "password2",
        "charlie": "password3",
    }

    model_config = SettingsConfigDict(extra="ignore")


# グローバルな設定インスタンス
settings = Settings()
