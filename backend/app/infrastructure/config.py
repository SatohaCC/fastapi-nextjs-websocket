"""アプリケーション設定モジュール。"""

from pathlib import Path
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from ..domain.primitives.primitives import Password, Username

_DEV_SECRET_KEY = "dev-secret-key-do-not-use-in-production"
_DEV_ADMIN_PASSWORD = "admin-password"
_DEV_ADMIN_SECRET_KEY = "dev-admin-secret-key"
_DEV_USERS: dict[Username, Password] = {
    Username("alice"): Password("password1"),
    Username("bob"): Password("password2"),
    Username("charlie"): Password("password3"),
}

# 起動時のカレントディレクトリに依存しないよう、backend/ 直下を絶対パスで指す
_BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """アプリケーション全体の設定を管理するクラス。

    優先順位（高い順）:
      1. 実際の環境変数
      2. .env.local（開発用ローカルファイル、Git 管理外）
    本番環境では APP_ENV=production を設定すること。
    デフォルト値のままのシークレットは本番起動時にエラーになります。
    """

    APP_ENV: Literal["development", "production"] = "development"

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
    SECRET_KEY: str = _DEV_SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ログインエンドポイントのレートリミット設定
    LOGIN_RATE_LIMIT_IP_MAX_ATTEMPTS: int = 10
    LOGIN_RATE_LIMIT_IP_WINDOW_SECONDS: int = 60
    LOGIN_RATE_LIMIT_USER_MAX_ATTEMPTS: int = 20
    LOGIN_RATE_LIMIT_USER_WINDOW_SECONDS: int = 900

    # SQLAdmin 設定
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = _DEV_ADMIN_PASSWORD
    ADMIN_SECRET_KEY: str = _DEV_ADMIN_SECRET_KEY

    # 簡易ユーザーマスター（デモ用）
    # key: username, value: password
    USERS: dict[Username, Password] = _DEV_USERS

    model_config = SettingsConfigDict(
        env_file=_BACKEND_DIR / ".env.local",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("USERS", mode="before")
    @classmethod
    def _coerce_users(cls, value: object) -> object:
        """環境変数の JSON をドメインプリミティブへ変換する。

        JSON ではキーにオブジェクトを使えないため、{"alice": "password1"} の
        ようなプレーンな文字列を受け取り Username/Password に包み直します。
        """
        if isinstance(value, dict):
            return {
                Username(k) if isinstance(k, str) else k: (
                    Password(v) if isinstance(v, str) else v
                )
                for k, v in value.items()
            }
        return value

    @model_validator(mode="after")
    def _reject_dev_secrets_in_production(self) -> "Settings":
        """本番環境でデフォルトのシークレットが使われていないことを検証する。"""
        if self.APP_ENV != "production":
            return self
        errors: list[str] = []
        if self.SECRET_KEY == _DEV_SECRET_KEY:
            errors.append("SECRET_KEY must be changed from the default value")
        if self.ADMIN_PASSWORD == _DEV_ADMIN_PASSWORD:
            errors.append("ADMIN_PASSWORD must be changed from the default value")
        if self.ADMIN_SECRET_KEY == _DEV_ADMIN_SECRET_KEY:
            errors.append("ADMIN_SECRET_KEY must be changed from the default value")
        if self.USERS == _DEV_USERS:
            errors.append("USERS must be replaced (demo users with known passwords)")
        if errors:
            raise ValueError(
                "Production secrets are not configured:\n"
                + "\n".join(f"  - {e}" for e in errors)
            )
        return self


# グローバルな設定インスタンス
settings = Settings()
