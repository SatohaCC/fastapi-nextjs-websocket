"""ユーザー認証とトークン発行を管理するアプリケーションサービス。"""

import json
import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import redis.asyncio as aioredis

from app.domain.entities.refresh_token import RefreshToken as RefreshTokenEntity
from app.domain.entities.user import User
from app.domain.entities.user_settings import UserSettings
from app.domain.exceptions import DomainValidationError
from app.domain.primitives.primitives import (
    AuthToken,
    HashedPassword,
    IpAddress,
    Password,
    RefreshToken,
    SessionId,
    UserAgent,
    UserId,
    Userid,
    Username,
)

from ..interfaces.auth import TokenProvider
from ..interfaces.password import PasswordVerifier
from ..outbox.delivery_feed import direct_request_sequence
from ..uow import UnitOfWork

logger = logging.getLogger(__name__)


class AuthService:
    """ユーザー認証とトークン発行を管理するアプリケーションサービス。"""

    def __init__(
        self,
        uow: UnitOfWork,
        jwt: TokenProvider,
        password_verifier: PasswordVerifier,
        refresh_token_expire_days: int,
        redis_client: aioredis.Redis | None = None,
    ) -> None:
        """認証サービスを初期化します。"""
        self._uow = uow
        self._jwt = jwt
        self._password_verifier = password_verifier
        self._refresh_token_expire_days = refresh_token_expire_days
        self._redis_client = redis_client

    async def register(
        self,
        userid: Userid,
        username: Username,
        password: Password,
    ) -> User:
        """新規ユーザーを登録し、初期設定を作成します。"""
        async with self._uow as uow:
            # 重複チェック
            existing = await uow.users.get_by_userid(userid)
            if existing is not None:
                raise DomainValidationError("ユーザーIDは既に登録されています。")

            # パスワードハッシュ化
            hashed = self._password_verifier.hash(password.value)
            user_id = uuid.uuid7()
            user = User(
                id=UserId(user_id),
                userid=userid,
                username=username,
                hashed_password=HashedPassword(hashed),
            )
            # 初期設定作成
            settings = UserSettings(
                user_id=user.id,
                global_chat=True,
                direct_request=True,
                direct_request_updated=True,
                browser_notification=False,
            )

            await uow.users.save(user)
            await uow.user_settings.upsert(settings)
            await uow.commit()
            return user

    async def login(
        self,
        userid: Userid,
        password: Password,
        ip_address: IpAddress | None = None,
        user_agent: UserAgent | None = None,
    ) -> tuple[AuthToken, RefreshToken] | None:
        """ユーザー認証を行い、成功した場合はトークンペアを返します。"""
        # ロックアウトチェック
        if self._redis_client:
            lockout_key = f"lockout:{userid.value}"
            is_locked = await self._redis_client.get(lockout_key)
            if is_locked:
                raise DomainValidationError(
                    "連続してログインに失敗したため、アカウントが一時的にロックされています。15分後に再試行してください。"
                )

        async with self._uow as uow:
            user = await uow.users.get_by_userid(userid)
            if user is None:
                # ユーザー不在時も失敗処理をして
                # タイミング攻撃やユーザー列挙を防ぐ
                await self._handle_failed_login(userid)
                return None

            if self._password_verifier.verify(
                password.value, user.hashed_password.value
            ):
                # ログイン成功時は失敗カウンターをリセット
                if self._redis_client:
                    attempts_key = f"login_attempts:{userid.value}"
                    await self._redis_client.delete(attempts_key)

                session_id = uuid.uuid7()
                access_token, refresh_token = self._jwt.create_token(
                    user.id, session_id
                )

                # リフレッシュトークンをDBに保存
                now = datetime.now(timezone.utc)
                expires_at = now + timedelta(days=self._refresh_token_expire_days)

                db_token = RefreshTokenEntity.create(
                    id=SessionId(session_id),
                    user_id=user.id,
                    token_value=refresh_token.value,
                    expires_at=expires_at,
                    created_at=now,
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
                await uow.refresh_tokens.save(db_token)
                await uow.commit()

                return access_token, refresh_token

            # パスワード不一致
            await self._handle_failed_login(userid)
            return None

    async def _handle_failed_login(self, userid: Userid) -> None:
        """ログイン失敗時の失敗カウンター処理およびロックアウト処理。"""
        if not self._redis_client:
            return

        attempts_key = f"login_attempts:{userid.value}"
        attempts = await self._redis_client.incr(attempts_key)
        if attempts == 1:
            await self._redis_client.expire(attempts_key, 3600)  # 有効期限 1 時間

        if attempts >= 5:
            lockout_key = f"lockout:{userid.value}"
            # 15分間ロックアウト
            await self._redis_client.set(lockout_key, "1", ex=900)
            await self._redis_client.delete(attempts_key)
            raise DomainValidationError(
                "連続してログインに失敗したため、アカウントが一時的にロックされています。15分後に再試行してください。"
            )

    async def delete_account(self, user_id: UserId) -> bool:
        """指定されたユーザー ID に対応するアカウントおよび全関連データを削除します。"""
        async with self._uow as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                return False

            # RESTRICT 制約を回避するため、関連メッセージとタスクを明示的に削除
            await uow.messages.delete_by_user_id(user_id)
            await uow.tasks.delete_by_user_id(user_id)

            # per-user inbox 用 SEQUENCE の後始末（カタログ肥大化防止）
            await uow.outbox.drop_sequence(direct_request_sequence(user.userid.value))

            # ユーザー本体削除（UserSettings, RefreshToken は CASCADE により自動削除）
            success = await uow.users.delete(user_id)
            await uow.commit()

        if success:
            # 即時セッション切断イベントを Redis Pub/Sub で通知
            await self._publish_force_disconnect(user_id)
        return success

    async def change_password(
        self,
        user_id: UserId,
        current_password: Password,
        new_password: Password,
    ) -> None:
        """パスワードを変更し、既存のセッションをすべて無効化します。"""
        async with self._uow as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                raise DomainValidationError("ユーザーが見つかりません。")

            # 現在のパスワード確認
            if not self._password_verifier.verify(
                current_password.value, user.hashed_password.value
            ):
                raise DomainValidationError("現在のパスワードが正しくありません。")

            # 新パスワードを設定
            hashed = self._password_verifier.hash(new_password.value)
            updated_user = User(
                id=user.id,
                userid=user.userid,
                username=user.username,
                hashed_password=HashedPassword(hashed),
            )
            await uow.users.save(updated_user)

            # すべてのアクティブセッションを無効化
            await uow.refresh_tokens.delete_by_user_id(user_id)
            await uow.commit()

        await self._publish_force_disconnect(user_id)

    async def forgot_password(
        self,
        userid: Userid,
    ) -> None:
        """パスワードリセット用トークンを発行し、メール送信をシミュレートします。"""
        async with self._uow as uow:
            user = await uow.users.get_by_userid(userid)

        # ユーザー列挙脆弱性対策のため、ユーザー不在でもエラーにしない
        if user is None:
            logger.warning(
                "Password reset requested for non-existing user: %s", userid.value
            )
            return

        token = secrets.token_urlsafe(32)
        if self._redis_client:
            token_key = f"password_reset:{token}"
            # 有効期限 15 分
            await self._redis_client.set(token_key, str(user.id.value), ex=900)
            logger.info(
                "PASSWORD RESET SIMULATION FOR USER %s: URL is http://localhost:3000/auth/reset-password?token=%s",
                userid.value,
                token,
            )
        else:
            logger.error(
                "Redis client is not configured. Password reset token cannot be saved."
            )

    async def reset_password(
        self,
        token: str,
        new_password: Password,
    ) -> None:
        """パスワードリセットトークンを用いてパスワードを再設定します。"""
        if not self._redis_client:
            raise DomainValidationError("Redisクライアントが設定されていません。")

        token_key = f"password_reset:{token}"
        user_id_str = await self._redis_client.get(token_key)
        if not user_id_str:
            raise DomainValidationError(
                "パスワードリセットトークンが無効または期限切れです。"
            )

        try:
            user_id = UserId(uuid.UUID(user_id_str))
        except ValueError:
            raise DomainValidationError("トークンに紐づくユーザー情報が不正です。")

        async with self._uow as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                raise DomainValidationError("ユーザーが見つかりません。")

            hashed = self._password_verifier.hash(new_password.value)
            updated_user = User(
                id=user.id,
                userid=user.userid,
                username=user.username,
                hashed_password=HashedPassword(hashed),
            )
            await uow.users.save(updated_user)

            # 既存セッションのクリア
            await uow.refresh_tokens.delete_by_user_id(user_id)
            await uow.commit()

        await self._redis_client.delete(token_key)
        await self._publish_force_disconnect(user_id)

    async def refresh(
        self,
        refresh_token: RefreshToken,
        ip_address: IpAddress | None = None,
        user_agent: UserAgent | None = None,
    ) -> tuple[AuthToken, RefreshToken] | None:
        """リフレッシュトークンを検証し、新しいトークンペアを返します。"""
        # JWTとしての形式・有効期限を検証
        user_id = self._jwt.verify_refresh_token(refresh_token)
        if user_id is None:
            return None

        hash_val = RefreshTokenEntity.hash_token(refresh_token.value)

        async with self._uow as uow:
            # DBにハッシュ値のレコードが存在するか確認
            db_token = await uow.refresh_tokens.get_by_hash(hash_val)
            if db_token is None:
                return None

            # DB上の有効期限チェック（安全のため）
            now = datetime.now(timezone.utc)
            if db_token.expires_at < now:
                await uow.refresh_tokens.delete_by_hash(hash_val)
                await uow.commit()
                return None

            # 古いリフレッシュトークンを物理削除
            await uow.refresh_tokens.delete_by_hash(hash_val)

            # 新しいトークンペアを発行（db_token.user_id を使用）
            new_session_id = uuid.uuid7()
            new_access_token, new_refresh_token = self._jwt.create_token(
                db_token.user_id, new_session_id
            )

            # 新しいリフレッシュトークンをDBに保存
            new_expires_at = now + timedelta(days=self._refresh_token_expire_days)

            new_db_token = RefreshTokenEntity.create(
                id=SessionId(new_session_id),
                user_id=db_token.user_id,
                token_value=new_refresh_token.value,
                expires_at=new_expires_at,
                created_at=now,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            await uow.refresh_tokens.save(new_db_token)
            await uow.commit()

            return new_access_token, new_refresh_token

    async def logout(self, refresh_token: RefreshToken) -> bool:
        """指定されたリフレッシュトークンをDBから物理削除します。"""
        user_id = self._jwt.verify_refresh_token(refresh_token)
        hash_val = RefreshTokenEntity.hash_token(refresh_token.value)
        async with self._uow as uow:
            success = await uow.refresh_tokens.delete_by_hash(hash_val)
            await uow.commit()
        if success and user_id:
            await self._publish_force_disconnect(user_id)
        return success

    def get_user_id_from_token(self, token: AuthToken) -> UserId | None:
        """アクセストークンを検証し、ユーザー ID を取得します。"""
        return self._jwt.verify_token(token)

    def get_session_id_from_token(self, token: AuthToken) -> SessionId | None:
        """アクセストークンからセッション ID を取得します。"""
        sid = self._jwt.get_session_id_from_token(token)
        return SessionId(sid) if sid else None

    async def get_user_by_id(self, user_id: UserId) -> User | None:
        """ユーザー ID でユーザーを取得します。"""
        async with self._uow as uow:
            return await uow.users.get_by_id(user_id)

    async def get_all_userids(self) -> list[Userid]:
        """全ログインIDを取得します。"""
        async with self._uow as uow:
            users = await uow.users.get_all()
            return [u.userid for u in users]

    async def get_all_users(self) -> list[User]:
        """全ユーザー情報を取得します。"""
        async with self._uow as uow:
            return await uow.users.get_all()

    async def get_active_sessions(self, user_id: UserId) -> list[RefreshTokenEntity]:
        """ユーザーのすべてのアクティブなセッション（リフレッシュトークン）を取得します。"""
        async with self._uow as uow:
            return await uow.refresh_tokens.get_by_user_id(user_id)

    async def revoke_session(self, user_id: UserId, token_id: SessionId) -> bool:
        """指定されたセッションを無効化（物理削除）します。"""
        async with self._uow as uow:
            token = await uow.refresh_tokens.get_by_id(token_id)
            if token is None or token.user_id != user_id:
                return False
            success = await uow.refresh_tokens.delete_by_id(token_id)
            await uow.commit()
        if success:
            # session_id を指定し、無効化された当該セッションの接続だけを切断する。
            # 他デバイスのセッションを巻き込んで誤ログアウトさせないため。
            await self._publish_force_disconnect(user_id, token_id)
        return success

    async def _publish_force_disconnect(
        self, user_id: UserId, session_id: SessionId | None = None
    ) -> None:
        """指定されたユーザーの強制切断イベントを
        Redis Pub/Sub にパブリッシュします。

        ``session_id`` を指定した場合は当該セッションの接続のみが対象になり、
        省略した場合はそのユーザーの全接続が対象になります。
        """
        if not self._redis_client:
            return

        try:
            payload: dict[str, str] = {
                "type": "force_disconnect",
                "user_id": str(user_id.value),
            }
            if session_id is not None:
                payload["session_id"] = str(session_id.value)
            await self._redis_client.publish("session_control", json.dumps(payload))
            logger.info("Published force_disconnect event for user %s", user_id.value)
        except Exception as e:
            logger.error("Failed to publish force_disconnect event: %s", e)

    async def _publish_reconnect(self, user_id: UserId) -> None:
        """指定されたユーザーの再接続イベントを
        Redis Pub/Sub にパブリッシュします。
        """
        if not self._redis_client:
            return

        try:
            payload = {
                "type": "reconnect",
                "user_id": str(user_id.value),
            }
            await self._redis_client.publish("session_control", json.dumps(payload))
            logger.info("Published reconnect event for user %s", user_id.value)
        except Exception as e:
            logger.error("Failed to publish reconnect event: %s", e)

    async def is_session_valid(self, token: AuthToken) -> bool:
        """アクセストークンに含まれるセッションが有効かどうかを検証します。"""
        sid = self._jwt.get_session_id_from_token(token)
        if sid is None:
            return False
        async with self._uow as uow:
            db_token = await uow.refresh_tokens.get_by_id(SessionId(sid))
            if db_token is None:
                return False
            now = datetime.now(timezone.utc)
            if db_token.expires_at < now:
                return False
            return True

    async def update_username(
        self,
        user_id: UserId,
        new_username: Username,
    ) -> User:
        """ユーザーの表示名（username）を変更し、関連する参照を更新の上、再接続を促します。"""
        async with self._uow as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                raise DomainValidationError("ユーザーが見つかりません。")

            old_username = user.username

            # 1. 関連テーブルを一括更新
            await uow.users.update_username(user_id, old_username, new_username)

            # 2. ユーザー自身の username を更新
            updated_user = User(
                id=user.id,
                userid=user.userid,
                username=new_username,
                hashed_password=user.hashed_password,
            )
            await uow.users.save(updated_user)
            await uow.commit()

        # 3. WebSocket 接続をクローズし、再接続を促す
        await self._publish_reconnect(user_id)
        return updated_user
