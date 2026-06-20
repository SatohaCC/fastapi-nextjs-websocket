"""Settings の本番環境バリデーションのユニットテスト。"""

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.domain.primitives.primitives import Password, Username
from app.infrastructure.config import (
    _DEV_ADMIN_PASSWORD,
    _DEV_ADMIN_SECRET_KEY,
    _DEV_SECRET_KEY,
    Settings,
)

PROD_SECRETS = {
    "SECRET_KEY": "a" * 64,
    "ADMIN_PASSWORD": "strong-admin-password",
    "ADMIN_SECRET_KEY": "b" * 64,
    "USERS": {"dave": "strong-user-password"},
}


def test_development_allows_default_secrets() -> None:
    """Development ではデフォルトシークレットのままでも起動できること。"""
    settings = Settings(_env_file=None, APP_ENV="development")

    assert settings.APP_ENV == "development"


def test_production_rejects_default_secrets() -> None:
    """Production でデフォルトシークレットが残っていると ValidationError になること。"""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            _env_file=None,
            APP_ENV="production",
            SECRET_KEY=_DEV_SECRET_KEY,
            ADMIN_PASSWORD=_DEV_ADMIN_PASSWORD,
            ADMIN_SECRET_KEY=_DEV_ADMIN_SECRET_KEY,
        )

    message = str(exc_info.value)
    assert "SECRET_KEY" in message
    assert "ADMIN_PASSWORD" in message
    assert "ADMIN_SECRET_KEY" in message
    assert "USERS" in message


def test_production_rejects_partial_default_secrets() -> None:
    """Production で一部だけデフォルトの場合、その項目のみ報告されること。"""
    secrets = {**PROD_SECRETS, "ADMIN_PASSWORD": _DEV_ADMIN_PASSWORD}

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None, APP_ENV="production", **secrets)

    message = str(exc_info.value)
    assert "ADMIN_PASSWORD" in message
    assert "SECRET_KEY must be changed" not in message


def test_production_accepts_configured_secrets() -> None:
    """Production でもすべてのシークレットが設定済みなら起動できること。"""
    settings = Settings(_env_file=None, APP_ENV="production", **PROD_SECRETS)

    assert settings.APP_ENV == "production"


def test_users_coerced_from_plain_json_mapping() -> None:
    """プレーンな {str: str} の USERS がドメインプリミティブに変換されること。

    環境変数の JSON ではキーにオブジェクトを使えないため、
    文字列のまま受け取って Username/Password に変換できる必要がある。
    """
    settings = Settings(_env_file=None, USERS={"dave": "s3cret"})

    assert settings.USERS == {Username("dave"): Password("s3cret")}


def test_env_file_path_is_absolute() -> None:
    """env_file が起動時のカレントディレクトリに依存しない絶対パスであること。"""
    env_file = Settings.model_config.get("env_file")

    assert isinstance(env_file, Path)
    assert env_file.is_absolute()
    assert env_file.name == ".env.local"
