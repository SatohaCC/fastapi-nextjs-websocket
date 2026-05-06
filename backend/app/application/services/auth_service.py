"""ユーザー認証とトークン発行を担うアプリケーションサービス。"""

from ...domain.repositories.jwt_service import JwtService


class AuthService:
    """ユーザー認証とトークン発行を管理するアプリケーションサービス。"""

    def __init__(self, jwt: JwtService, users: dict[str, str]) -> None:
        """認証サービスを初期化します。"""
        self._jwt = jwt
        self._users = users

    def login(self, username: str, password: str) -> str | None:
        """ユーザー認証を行い、成功した場合は JWT トークンを返します。"""
        if self._jwt.authenticate_user(username, password):
            return self._jwt.create_token(username)
        return None

    def get_user_from_token(self, token: str) -> str | None:
        """トークンを検証し、ユーザー名を取得します。"""
        return self._jwt.verify_token(token)

    def get_all_usernames(self) -> list[str]:
        """全ユーザー名を取得します。"""
        return list(self._users.keys())
