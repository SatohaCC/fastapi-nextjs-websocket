"""PyJWT を使用した JWT 認証サービスの実装。"""

import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.domain.primitives.primitives import AuthToken, RefreshToken, UserId

from ..config import settings

_ACCESS_TYPE = "access"
_REFRESH_TYPE = "refresh"


class JwtServiceImpl:
    """JwtService の実装。"""

    def create_token(
        self, user_id: UserId, session_id: uuid.UUID | None = None
    ) -> tuple[AuthToken, RefreshToken]:
        """ユーザー ID に基づきトークンペアを生成して返します。"""
        now = datetime.now(timezone.utc)
        sid = session_id or uuid.uuid7()

        access_payload = {
            "sub": str(user_id.value),
            "type": _ACCESS_TYPE,
            "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "jti": str(uuid.uuid7()),
            "sid": str(sid),
        }
        access_token = AuthToken(
            jwt.encode(
                access_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
            )
        )

        refresh_payload = {
            "sub": str(user_id.value),
            "type": _REFRESH_TYPE,
            "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            "jti": str(uuid.uuid7()),
            "sid": str(sid),
        }
        refresh_token = RefreshToken(
            jwt.encode(
                refresh_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
            )
        )

        return access_token, refresh_token

    def verify_token(self, token: AuthToken) -> UserId | None:
        """アクセストークンを検証しユーザー ID を返します。"""
        try:
            payload = jwt.decode(
                token.value, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            if payload.get("type") != _ACCESS_TYPE:
                return None
            sub: str | None = payload.get("sub")
            if sub is None:
                return None
            return UserId(uuid.UUID(sub))
        except jwt.PyJWTError, ValueError:
            return None

    def verify_refresh_token(self, token: RefreshToken) -> UserId | None:
        """リフレッシュトークンを検証しユーザー ID を返します。"""
        try:
            payload = jwt.decode(
                token.value, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            if payload.get("type") != _REFRESH_TYPE:
                return None
            sub: str | None = payload.get("sub")
            if sub is None:
                return None
            return UserId(uuid.UUID(sub))
        except jwt.PyJWTError, ValueError:
            return None

    def get_session_id_from_token(self, token: AuthToken) -> uuid.UUID | None:
        """アクセストークンからセッション ID (sid) を取得します。"""
        try:
            payload = jwt.decode(
                token.value, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            sid = payload.get("sid")
            if sid is None:
                return None
            return uuid.UUID(sid)
        except jwt.PyJWTError, ValueError:
            return None
