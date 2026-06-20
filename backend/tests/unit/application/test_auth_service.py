"""AuthService のユニットテスト（UoW / Repository をモック化）。"""

import uuid
from unittest.mock import ANY, AsyncMock, MagicMock

import pytest

from app.application.services.auth_service import AuthService
from app.domain.entities.user import User
from app.domain.exceptions import DomainValidationError
from app.domain.primitives.primitives import (
    AuthToken,
    HashedPassword,
    Password,
    RefreshToken,
    SessionId,
    UserId,
    Userid,
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
        userid = Userid("alice")
        username = Username("alice")
        password = Password("password1")
        hashed_password = PasswordHasher.hash_password(password.value)

        mock_user = User(
            id=ALICE_ID,
            userid=userid,
            username=username,
            hashed_password=HashedPassword(hashed_password),
        )
        mock_uow.users.get_by_userid.return_value = mock_user

        service = AuthService(
            mock_uow, mock_jwt, PasswordHasher(), refresh_token_expire_days=7
        )
        result = await service.login(userid, password)

        assert result is not None
        assert result[0].value == "mock_access_token"
        assert result[1].value == "mock_refresh_token"
        mock_uow.users.get_by_userid.assert_called_once_with(userid)
        # create_token は user.id（UUID）と session_id で呼ばれる
        mock_jwt.create_token.assert_called_once_with(ALICE_ID, ANY)

    async def test_login_failure_user_not_found(self, mock_uow, mock_jwt):
        """ユーザーが存在しない場合、ログイン失敗（None が返る）を確認。"""
        mock_uow.users.get_by_userid.return_value = None

        service = AuthService(
            mock_uow, mock_jwt, PasswordHasher(), refresh_token_expire_days=7
        )
        result = await service.login(Userid("unknown"), Password("password1"))

        assert result is None
        mock_jwt.create_token.assert_not_called()

    async def test_login_failure_incorrect_password(self, mock_uow, mock_jwt):
        """パスワードが不一致の場合、ログイン失敗（None が返る）を確認。"""
        userid = Userid("alice")
        username = Username("alice")
        correct_password_hashed = PasswordHasher.hash_password("correct_password")

        mock_user = User(
            id=ALICE_ID,
            userid=userid,
            username=username,
            hashed_password=HashedPassword(correct_password_hashed),
        )
        mock_uow.users.get_by_userid.return_value = mock_user

        service = AuthService(
            mock_uow, mock_jwt, PasswordHasher(), refresh_token_expire_days=7
        )
        result = await service.login(userid, Password("wrong_password"))

        assert result is None
        mock_jwt.create_token.assert_not_called()


@pytest.mark.asyncio
class TestAuthServiceGetAllUserids:
    """AuthService.get_all_userids のテスト。"""

    async def test_returns_all_userids(self, mock_uow, mock_jwt):
        """登録されているすべてのログインIDが返ることを確認。"""
        users = [
            User(
                id=UserId(uuid.uuid7()),
                userid=Userid("alice"),
                username=Username("alice"),
                hashed_password=HashedPassword("$2b$hashed_1"),
            ),
            User(
                id=UserId(uuid.uuid7()),
                userid=Userid("bob"),
                username=Username("bob"),
                hashed_password=HashedPassword("$2b$hashed_2"),
            ),
        ]
        mock_uow.users.get_all.return_value = users

        service = AuthService(
            mock_uow, mock_jwt, PasswordHasher(), refresh_token_expire_days=7
        )
        result = await service.get_all_userids()

        assert len(result) == 2
        assert Userid("alice") in result
        assert Userid("bob") in result
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

    async def test_logout_publishes_force_disconnect(self, mock_uow, mock_jwt):
        """ログアウト成功時、Redis に強制切断イベントがパブリッシュされることを検証。"""
        refresh_token = RefreshToken("mock_refresh_token")
        mock_uow.refresh_tokens.delete_by_hash.return_value = True
        mock_redis_client = AsyncMock()

        service = AuthService(
            mock_uow,
            mock_jwt,
            PasswordHasher(),
            refresh_token_expire_days=7,
            redis_client=mock_redis_client,
        )
        result = await service.logout(refresh_token)

        assert result is True
        mock_redis_client.publish.assert_awaited_once()
        args, _ = mock_redis_client.publish.call_args
        assert args[0] == "session_control"
        import json

        payload = json.loads(args[1])
        assert payload["type"] == "force_disconnect"
        assert payload["user_id"] == str(ALICE_ID.value)


@pytest.mark.asyncio
class TestAuthServiceSessions:
    """AuthService セッション管理機能のテスト。"""

    async def test_get_active_sessions(self, mock_uow, mock_jwt):
        """ユーザーに紐づくセッション一覧が正しく取得できることを確認。"""
        mock_uow.refresh_tokens.get_by_user_id.return_value = ["session1", "session2"]

        service = AuthService(
            mock_uow, mock_jwt, PasswordHasher(), refresh_token_expire_days=7
        )
        result = await service.get_active_sessions(ALICE_ID)

        assert result == ["session1", "session2"]
        mock_uow.refresh_tokens.get_by_user_id.assert_called_once_with(ALICE_ID)

    async def test_revoke_session_success(self, mock_uow, mock_jwt):
        """トークンが存在し所有者が一致する場合、無効化（削除）が成功することを確認。"""
        token_id = SessionId(uuid.uuid7())
        mock_token = MagicMock()
        mock_token.user_id = ALICE_ID
        mock_uow.refresh_tokens.get_by_id.return_value = mock_token
        mock_uow.refresh_tokens.delete_by_id.return_value = True

        service = AuthService(
            mock_uow, mock_jwt, PasswordHasher(), refresh_token_expire_days=7
        )
        result = await service.revoke_session(ALICE_ID, token_id)

        assert result is True
        mock_uow.refresh_tokens.get_by_id.assert_called_once_with(token_id)
        mock_uow.refresh_tokens.delete_by_id.assert_called_once_with(token_id)
        mock_uow.commit.assert_called_once()

    async def test_revoke_session_publishes_force_disconnect(self, mock_uow, mock_jwt):
        """セッション無効化成功時に Redis イベントをパブリッシュする検証。"""
        token_id = SessionId(uuid.uuid7())
        mock_token = MagicMock()
        mock_token.user_id = ALICE_ID
        mock_uow.refresh_tokens.get_by_id.return_value = mock_token
        mock_uow.refresh_tokens.delete_by_id.return_value = True
        mock_redis_client = AsyncMock()

        service = AuthService(
            mock_uow,
            mock_jwt,
            PasswordHasher(),
            refresh_token_expire_days=7,
            redis_client=mock_redis_client,
        )
        result = await service.revoke_session(ALICE_ID, token_id)

        assert result is True
        mock_redis_client.publish.assert_awaited_once()
        args, _ = mock_redis_client.publish.call_args
        assert args[0] == "session_control"
        import json

        payload = json.loads(args[1])
        assert payload["type"] == "force_disconnect"
        assert payload["user_id"] == str(ALICE_ID.value)
        # 他デバイスのセッションを巻き込まないよう、session_id を伴う必要がある
        assert payload["session_id"] == str(token_id)

    async def test_revoke_session_failure_not_found(self, mock_uow, mock_jwt):
        """トークンが存在しない場合、無効化が失敗（False）することを確認。"""
        token_id = SessionId(uuid.uuid7())
        mock_uow.refresh_tokens.get_by_id.return_value = None

        service = AuthService(
            mock_uow, mock_jwt, PasswordHasher(), refresh_token_expire_days=7
        )
        result = await service.revoke_session(ALICE_ID, token_id)

        assert result is False
        mock_uow.refresh_tokens.get_by_id.assert_called_once_with(token_id)
        mock_uow.refresh_tokens.delete_by_id.assert_not_called()
        mock_uow.commit.assert_not_called()

    async def test_revoke_session_failure_owner_mismatch(self, mock_uow, mock_jwt):
        """他人のトークンを無効化しようとした場合、失敗（False）することを確認。"""
        token_id = SessionId(uuid.uuid7())
        mock_token = MagicMock()
        mock_token.user_id = UserId(uuid.uuid7())  # 他のユーザーID
        mock_uow.refresh_tokens.get_by_id.return_value = mock_token

        service = AuthService(
            mock_uow, mock_jwt, PasswordHasher(), refresh_token_expire_days=7
        )
        result = await service.revoke_session(ALICE_ID, token_id)

        assert result is False
        mock_uow.refresh_tokens.get_by_id.assert_called_once_with(token_id)
        mock_uow.refresh_tokens.delete_by_id.assert_not_called()
        mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
class TestAuthServiceRegister:
    """AuthService.register のテスト。"""

    async def test_register_success(self, mock_uow, mock_jwt):
        """新規ユーザーが正常に登録され、初期設定が作成されることを確認。"""
        userid = Userid("bob")
        username = Username("Bob Name")
        password = Password("password123")
        mock_uow.users.get_by_userid.return_value = None

        service = AuthService(
            mock_uow, mock_jwt, PasswordHasher(), refresh_token_expire_days=7
        )
        user = await service.register(userid, username, password)

        assert user is not None
        assert user.userid == userid
        assert user.username == username
        mock_uow.users.save.assert_called_once()
        mock_uow.user_settings.upsert.assert_called_once()
        mock_uow.commit.assert_called_once()

    async def test_register_duplicate_username(self, mock_uow, mock_jwt):
        """すでに存在するユーザー名で登録しようとした場合、例外が送出されることを確認。"""
        userid = Userid("alice")
        username = Username("Alice Name")
        password = Password("password123")
        mock_uow.users.get_by_userid.return_value = MagicMock()

        service = AuthService(
            mock_uow, mock_jwt, PasswordHasher(), refresh_token_expire_days=7
        )
        with pytest.raises(
            DomainValidationError, match="ユーザーIDは既に登録されています。"
        ):
            await service.register(userid, username, password)

        mock_uow.users.save.assert_not_called()
        mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
class TestAuthServiceDeleteAccount:
    """AuthService.delete_account のテスト。"""

    async def test_delete_account_success(self, mock_uow, mock_jwt):
        """アカウント削除が正常に行われ、関連データが削除され、強制切断イベントがパブリッシュされることを確認。"""
        user_id = ALICE_ID
        mock_user = MagicMock()
        mock_uow.users.get_by_id.return_value = mock_user
        mock_uow.users.delete.return_value = True
        mock_redis_client = AsyncMock()

        service = AuthService(
            mock_uow,
            mock_jwt,
            PasswordHasher(),
            refresh_token_expire_days=7,
            redis_client=mock_redis_client,
        )
        success = await service.delete_account(user_id)

        assert success is True
        mock_uow.messages.delete_by_user_id.assert_called_once_with(user_id)
        mock_uow.tasks.delete_by_user_id.assert_called_once_with(user_id)
        mock_uow.users.delete.assert_called_once_with(user_id)
        mock_uow.commit.assert_called_once()
        mock_redis_client.publish.assert_awaited_once()

    async def test_delete_account_user_not_found(self, mock_uow, mock_jwt):
        """ユーザーが見つからない場合、削除を行わず False を返すことを確認。"""
        user_id = ALICE_ID
        mock_uow.users.get_by_id.return_value = None

        service = AuthService(
            mock_uow, mock_jwt, PasswordHasher(), refresh_token_expire_days=7
        )
        success = await service.delete_account(user_id)

        assert success is False
        mock_uow.messages.delete_by_user_id.assert_not_called()
        mock_uow.tasks.delete_by_user_id.assert_not_called()
        mock_uow.users.delete.assert_not_called()
        mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
class TestAuthServiceChangePassword:
    """AuthService.change_password のテスト。"""

    async def test_change_password_success(self, mock_uow, mock_jwt):
        """パスワード変更が成功し、すべてのセッションが削除され、強制切断が呼ばれることを確認。"""
        user_id = ALICE_ID
        current_pwd = Password("current_password")
        new_pwd = Password("new_password123")
        hashed_password = PasswordHasher.hash_password(current_pwd.value)

        mock_user = User(
            id=user_id,
            userid=Userid("alice"),
            username=Username("alice"),
            hashed_password=HashedPassword(hashed_password),
        )
        mock_uow.users.get_by_id.return_value = mock_user
        mock_redis_client = AsyncMock()

        service = AuthService(
            mock_uow,
            mock_jwt,
            PasswordHasher(),
            refresh_token_expire_days=7,
            redis_client=mock_redis_client,
        )
        await service.change_password(user_id, current_pwd, new_pwd)

        mock_uow.users.save.assert_called_once()
        mock_uow.refresh_tokens.delete_by_user_id.assert_called_once_with(user_id)
        mock_uow.commit.assert_called_once()
        mock_redis_client.publish.assert_awaited_once()

    async def test_change_password_wrong_current(self, mock_uow, mock_jwt):
        """現在のパスワードが異なる場合、例外が送出されることを確認。"""
        user_id = ALICE_ID
        current_pwd = Password("wrong_password")
        new_pwd = Password("new_password123")
        hashed_password = PasswordHasher.hash_password("correct_password")

        mock_user = User(
            id=user_id,
            userid=Userid("alice"),
            username=Username("alice"),
            hashed_password=HashedPassword(hashed_password),
        )
        mock_uow.users.get_by_id.return_value = mock_user

        service = AuthService(
            mock_uow, mock_jwt, PasswordHasher(), refresh_token_expire_days=7
        )
        with pytest.raises(
            DomainValidationError, match="現在のパスワードが正しくありません。"
        ):
            await service.change_password(user_id, current_pwd, new_pwd)

        mock_uow.users.save.assert_not_called()
        mock_uow.refresh_tokens.delete_by_user_id.assert_not_called()
        mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
class TestAuthServiceUpdateUsername:
    """AuthService.update_username のテスト。"""

    async def test_update_username_success(self, mock_uow, mock_jwt):
        """ユーザーID（ハンドル）の更新が正常に成功することを確認。"""
        user_id = ALICE_ID
        new_username = Username("alice_new")
        mock_user = User(
            id=user_id,
            userid=Userid("alice"),
            username=Username("alice"),
            hashed_password=HashedPassword("$2b$hashed"),
        )
        mock_uow.users.get_by_id.return_value = mock_user
        mock_redis_client = AsyncMock()

        service = AuthService(
            mock_uow,
            mock_jwt,
            PasswordHasher(),
            refresh_token_expire_days=7,
            redis_client=mock_redis_client,
        )
        updated = await service.update_username(user_id, new_username)

        assert updated.username == new_username
        mock_uow.users.update_username.assert_called_once_with(
            user_id, mock_user.username, new_username
        )
        mock_uow.users.save.assert_called_once()
        mock_uow.commit.assert_called_once()
        mock_redis_client.publish.assert_awaited_once()

    async def test_update_username_duplicate(self, mock_uow, mock_jwt):
        """表示名の変更は重複チェックを行わないため、重複確認は不要。"""
        user_id = ALICE_ID
        new_username = Username("bob")
        mock_user = User(
            id=user_id,
            userid=Userid("alice"),
            username=Username("alice"),
            hashed_password=HashedPassword("$2b$hashed"),
        )
        mock_uow.users.get_by_id.return_value = mock_user

        service = AuthService(
            mock_uow, mock_jwt, PasswordHasher(), refresh_token_expire_days=7
        )
        # 例外がスローされないことをテスト
        updated = await service.update_username(user_id, new_username)
        assert updated.username == new_username


@pytest.mark.asyncio
class TestAuthServiceForgotPassword:
    """AuthService.forgot_password のテスト。"""

    async def test_forgot_password_success(self, mock_uow, mock_jwt):
        """ユーザーが存在する場合、トークンが Redis に保存されることを確認。"""
        userid = Userid("alice")
        mock_user = User(
            id=ALICE_ID,
            userid=userid,
            username=Username("alice"),
            hashed_password=HashedPassword("$2b$hashed"),
        )
        mock_uow.users.get_by_userid.return_value = mock_user
        mock_redis_client = AsyncMock()

        service = AuthService(
            mock_uow,
            mock_jwt,
            PasswordHasher(),
            refresh_token_expire_days=7,
            redis_client=mock_redis_client,
        )
        await service.forgot_password(userid)

        mock_redis_client.set.assert_called_once()
        args, kwargs = mock_redis_client.set.call_args
        assert args[0].startswith("password_reset:")
        assert args[1] == str(ALICE_ID.value)
        assert kwargs.get("ex") == 900

    async def test_forgot_password_user_not_found(self, mock_uow, mock_jwt):
        """ユーザーが存在しない場合、何もしない（例外も吐かない）ことを確認。"""
        userid = Userid("unknown")
        mock_uow.users.get_by_userid.return_value = None
        mock_redis_client = AsyncMock()

        service = AuthService(
            mock_uow,
            mock_jwt,
            PasswordHasher(),
            refresh_token_expire_days=7,
            redis_client=mock_redis_client,
        )
        await service.forgot_password(userid)

        mock_redis_client.set.assert_not_called()


@pytest.mark.asyncio
class TestAuthServiceResetPassword:
    """AuthService.reset_password のテスト。"""

    async def test_reset_password_success(self, mock_uow, mock_jwt):
        """有効なトークンでパスワードが正常に更新されることを確認。"""
        token = "valid_token"
        new_pwd = Password("new_password123")
        mock_redis_client = AsyncMock()
        mock_redis_client.get.return_value = str(ALICE_ID.value)

        mock_user = User(
            id=ALICE_ID,
            userid=Userid("alice"),
            username=Username("alice"),
            hashed_password=HashedPassword("$2b$hashed_old"),
        )
        mock_uow.users.get_by_id.return_value = mock_user

        service = AuthService(
            mock_uow,
            mock_jwt,
            PasswordHasher(),
            refresh_token_expire_days=7,
            redis_client=mock_redis_client,
        )
        await service.reset_password(token, new_pwd)

        mock_uow.users.save.assert_called_once()
        mock_uow.refresh_tokens.delete_by_user_id.assert_called_once_with(ALICE_ID)
        mock_uow.commit.assert_called_once()
        mock_redis_client.delete.assert_called_once_with(f"password_reset:{token}")
        mock_redis_client.publish.assert_awaited_once()

    async def test_reset_password_invalid_token(self, mock_uow, mock_jwt):
        """トークンが無効な場合、例外が送出されることを確認。"""
        token = "invalid_token"
        new_pwd = Password("new_password123")
        mock_redis_client = AsyncMock()
        mock_redis_client.get.return_value = None

        service = AuthService(
            mock_uow,
            mock_jwt,
            PasswordHasher(),
            refresh_token_expire_days=7,
            redis_client=mock_redis_client,
        )
        with pytest.raises(
            DomainValidationError,
            match="パスワードリセットトークンが無効または期限切れです。",
        ):
            await service.reset_password(token, new_pwd)

        mock_uow.users.save.assert_not_called()
        mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
class TestAuthServiceLockout:
    """AuthService ログインロックアウト機能のテスト。"""

    async def test_lockout_after_5_failures(self, mock_uow, mock_jwt):
        """5回連続でログインに失敗した時、アカウントがロックアウトされることを確認。"""
        userid = Userid("alice")
        password = Password("wrong_password")
        correct_password_hashed = PasswordHasher.hash_password("correct_password")

        mock_user = User(
            id=ALICE_ID,
            userid=userid,
            username=Username("alice"),
            hashed_password=HashedPassword(correct_password_hashed),
        )
        mock_uow.users.get_by_userid.return_value = mock_user

        mock_redis_client = AsyncMock()
        # ロックアウトチェックは未ロック
        mock_redis_client.get.return_value = None

        service = AuthService(
            mock_uow,
            mock_jwt,
            PasswordHasher(),
            refresh_token_expire_days=7,
            redis_client=mock_redis_client,
        )

        # 4回目までは None が返る (かつ incr が呼ばれる)
        mock_redis_client.incr.return_value = 1
        res = await service.login(userid, password)
        assert res is None

        mock_redis_client.incr.return_value = 4
        res = await service.login(userid, password)
        assert res is None

        # 5回目のログイン失敗でロックアウト例外が送出されることを確認
        mock_redis_client.incr.return_value = 5
        with pytest.raises(
            DomainValidationError, match="アカウントが一時的にロックされています"
        ):
            await service.login(userid, password)

        mock_redis_client.set.assert_called_once_with(
            f"lockout:{userid.value}", "1", ex=900
        )
        mock_redis_client.delete.assert_called_once_with(
            f"login_attempts:{userid.value}"
        )

    async def test_cannot_login_when_locked(self, mock_uow, mock_jwt):
        """すでにロックアウトされているユーザーがログインしようとした場合、最初から例外を吐くことを確認。"""
        userid = Userid("alice")
        password = Password("password123")
        mock_redis_client = AsyncMock()
        # ロックアウトが存在する状態をモック
        mock_redis_client.get.return_value = "1"

        service = AuthService(
            mock_uow,
            mock_jwt,
            PasswordHasher(),
            refresh_token_expire_days=7,
            redis_client=mock_redis_client,
        )

        with pytest.raises(
            DomainValidationError, match="アカウントが一時的にロックされています"
        ):
            await service.login(userid, password)

        mock_uow.users.get_by_userid.assert_not_called()
