"""AuthService のユニットテスト（UoW / Repository をモック化）。"""

import uuid
from unittest.mock import MagicMock

import pytest

from app.application.services.auth_service import AuthService
from app.domain.entities.user import User
from app.domain.primitives.primitives import (
    AuthToken,
    Password,
    RefreshToken,
    UserId,
    Username,
)
from app.infrastructure.auth.password_hasher import PasswordHasher

ALICE_ID = UserId(uuid.uuid7())


@pytest.fixture
def mock_jwt():
    """TokenProvider のモック。"""
    jwt = MagicMock()
    jwt.create_token.return_value = (
        AuthToken("mock_access_token"),
        RefreshToken("mock_refresh_token"),
    )
    jwt.verify_refresh_token.return_value = ALICE_ID
    jwt.verify_token.return_value = ALICE_ID
    return jwt


@pytest.mark.asyncio
class TestAuthServiceLogin:
    """AuthService.login のテスト。"""

    async def test_login_success(self, mock_uow, mock_jwt):
        """パスワードが一致する場合、ログイン成功しトークンペアが返ることを確認。"""
        username = Username("alice")
        password = Password("password1")
        hashed_password = PasswordHasher.hash_password(password.value)

        mock_user = User(
            id=ALICE_ID, username=username, hashed_password=hashed_password
        )
        mock_uow.users.get_by_username.return_value = mock_user

        service = AuthService(
            mock_uow, mock_jwt, PasswordHasher(), refresh_token_expire_days=7
        )
        result = await service.login(username, password)

        assert result is not None
        assert result[0].value == "mock_access_token"
        assert result[1].value == "mock_refresh_token"
        mock_uow.users.get_by_username.assert_called_once_with(username)
        # create_token は user.id（UUID）で呼ばれる
        mock_jwt.create_token.assert_called_once_with(ALICE_ID)

    async def test_login_failure_user_not_found(self, mock_uow, mock_jwt):
        """ユーザーが存在しない場合、ログイン失敗（None が返る）を確認。"""
        mock_uow.users.get_by_username.return_value = None

        service = AuthService(
            mock_uow, mock_jwt, PasswordHasher(), refresh_token_expire_days=7
        )
        result = await service.login(Username("unknown"), Password("password1"))

        assert result is None
        mock_jwt.create_token.assert_not_called()

    async def test_login_failure_incorrect_password(self, mock_uow, mock_jwt):
        """パスワードが不一致の場合、ログイン失敗（None が返る）を確認。"""
        username = Username("alice")
        correct_password_hashed = PasswordHasher.hash_password("correct_password")

        mock_user = User(
            id=ALICE_ID,
            username=username,
            hashed_password=correct_password_hashed,
        )
        mock_uow.users.get_by_username.return_value = mock_user

        service = AuthService(
            mock_uow, mock_jwt, PasswordHasher(), refresh_token_expire_days=7
        )
        result = await service.login(username, Password("wrong_password"))

        assert result is None
        mock_jwt.create_token.assert_not_called()


@pytest.mark.asyncio
class TestAuthServiceGetAllUsernames:
    """AuthService.get_all_usernames のテスト。"""

    async def test_returns_all_usernames(self, mock_uow, mock_jwt):
        """登録されているすべてのユーザー名が返ることを確認。"""
        users = [
            User(
                id=UserId(uuid.uuid7()),
                username=Username("alice"),
                hashed_password="hashed_1",
            ),
            User(
                id=UserId(uuid.uuid7()),
                username=Username("bob"),
                hashed_password="hashed_2",
            ),
        ]
        mock_uow.users.get_all.return_value = users

        service = AuthService(
            mock_uow, mock_jwt, PasswordHasher(), refresh_token_expire_days=7
        )
        result = await service.get_all_usernames()

        assert len(result) == 2
        assert Username("alice") in result
        assert Username("bob") in result
        mock_uow.users.get_all.assert_called_once()


@pytest.mark.asyncio
class TestAuthServiceRefresh:
    """AuthService.refresh のテスト。"""

    async def test_refresh_success(self, mock_uow, mock_jwt):
        """有効なリフレッシュトークンの場合、古いトークンが削除され、新しいトークンペアが返ることを確認。"""
        refresh_token = RefreshToken("mock_refresh_token")

        # モックDBトークンの用意
        mock_db_token = MagicMock()
        mock_db_token.user_id = ALICE_ID
        # 現在より未来の有効期限
        from datetime import datetime, timedelta, timezone

        mock_db_token.expires_at = datetime.now(timezone.utc) + timedelta(days=1)

        mock_uow.refresh_tokens.get_by_hash.return_value = mock_db_token

        service = AuthService(
            mock_uow, mock_jwt, PasswordHasher(), refresh_token_expire_days=7
        )
        result = await service.refresh(refresh_token)

        assert result is not None
        assert result[0].value == "mock_access_token"
        assert result[1].value == "mock_refresh_token"

        mock_uow.refresh_tokens.get_by_hash.assert_called_once()
        mock_uow.refresh_tokens.delete_by_hash.assert_called_once()
        mock_uow.refresh_tokens.save.assert_called_once()
        mock_uow.commit.assert_called_once()

    async def test_refresh_failure_token_not_found_in_db(self, mock_uow, mock_jwt):
        """DBにトークンがない場合、リフレッシュ失敗(Noneが返る)を確認。"""
        refresh_token = RefreshToken("mock_refresh_token")
        mock_uow.refresh_tokens.get_by_hash.return_value = None

        service = AuthService(
            mock_uow, mock_jwt, PasswordHasher(), refresh_token_expire_days=7
        )
        result = await service.refresh(refresh_token)

        assert result is None
        mock_uow.refresh_tokens.delete_by_hash.assert_not_called()
        mock_uow.refresh_tokens.save.assert_not_called()

    async def test_refresh_failure_token_expired(self, mock_uow, mock_jwt):
        """DB上のトークンが期限切れの場合、古いトークンを削除しリフレッシュが失敗（None）することを確認。"""
        refresh_token = RefreshToken("mock_refresh_token")

        mock_db_token = MagicMock()
        mock_db_token.user_id = ALICE_ID
        # 過去の有効期限
        from datetime import datetime, timedelta, timezone

        mock_db_token.expires_at = datetime.now(timezone.utc) - timedelta(days=1)

        mock_uow.refresh_tokens.get_by_hash.return_value = mock_db_token

        service = AuthService(
            mock_uow, mock_jwt, PasswordHasher(), refresh_token_expire_days=7
        )
        result = await service.refresh(refresh_token)

        assert result is None
        mock_uow.refresh_tokens.delete_by_hash.assert_called_once()
        mock_uow.refresh_tokens.save.assert_not_called()
        mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
class TestAuthServiceLogout:
    """AuthService.logout のテスト。"""

    async def test_logout_success(self, mock_uow, mock_jwt):
        """ログアウト処理が呼び出された際、DBからトークンが削除され、Trueが返ることを確認。"""
        refresh_token = RefreshToken("mock_refresh_token")
        mock_uow.refresh_tokens.delete_by_hash.return_value = True

        service = AuthService(
            mock_uow, mock_jwt, PasswordHasher(), refresh_token_expire_days=7
        )
        result = await service.logout(refresh_token)

        assert result is True
        mock_uow.refresh_tokens.delete_by_hash.assert_called_once()
        mock_uow.commit.assert_called_once()
