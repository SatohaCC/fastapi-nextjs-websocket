"""JwtServiceImpl のユニットテスト。"""

import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.domain.primitives.primitives import AuthToken, RefreshToken, UserId
from app.infrastructure.auth.jwt_service import JwtServiceImpl
from app.infrastructure.config import settings


def _make_user_id() -> UserId:
    return UserId(uuid.uuid7())


def test_verify_token_round_trip() -> None:
    """create_token で生成したアクセストークンを検証すると元の UserId が返ること。"""
    service = JwtServiceImpl()
    user_id = _make_user_id()

    access_token, _ = service.create_token(user_id)

    assert service.verify_token(access_token) == user_id


def test_verify_token_rejects_invalid_token() -> None:
    """不正な文字列のアクセストークンは None になること。"""
    service = JwtServiceImpl()

    assert service.verify_token(AuthToken("not-a-jwt")) is None


def test_verify_token_rejects_refresh_token() -> None:
    """リフレッシュトークンを verify_token に渡すと type 不一致で None になること。"""
    service = JwtServiceImpl()
    _, refresh_token = service.create_token(_make_user_id())

    assert service.verify_token(AuthToken(refresh_token.value)) is None


def test_verify_token_rejects_non_uuid_sub() -> None:
    """Sub が UUID でないトークンは None になること。"""
    service = JwtServiceImpl()
    payload = {
        "sub": "not-a-uuid",
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        "jti": str(uuid.uuid7()),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    assert service.verify_token(AuthToken(token)) is None


def test_verify_refresh_token_round_trip() -> None:
    """リフレッシュトークンを検証すると元の UserId が返ること。"""
    service = JwtServiceImpl()
    user_id = _make_user_id()

    _, refresh_token = service.create_token(user_id)

    assert service.verify_refresh_token(refresh_token) == user_id


def test_verify_refresh_token_rejects_invalid_token() -> None:
    """不正な文字列のリフレッシュトークンは None になること。"""
    service = JwtServiceImpl()

    assert service.verify_refresh_token(RefreshToken("not-a-jwt")) is None


def test_verify_refresh_token_rejects_access_token() -> None:
    """アクセストークンを渡すと type 不一致で None になること。"""
    service = JwtServiceImpl()
    access_token, _ = service.create_token(_make_user_id())

    assert service.verify_refresh_token(RefreshToken(access_token.value)) is None
