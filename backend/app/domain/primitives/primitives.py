"""アプリケーションで使用するドメインプリミティブの定義。"""

import ipaddress
import re
import uuid

from ..exceptions import DomainValidationError
from .base import DomainPrimitive


class EntityId(DomainPrimitive[int]):
    """エンティティの一意識別子。"""

    def validate(self):
        """バリデーションルールを適用します。"""
        if self.value < 0:
            raise DomainValidationError("EntityId must be non-negative")


class UserId(DomainPrimitive[uuid.UUID]):
    """ユーザーの一意識別子（UUIDv7）を表すドメインプリミティブ。"""

    def validate(self):
        """バリデーションルールを適用します。"""
        if self.value.version != 7:
            raise DomainValidationError("UserId must be a UUID v7")


class Userid(DomainPrimitive[str]):
    """ログインIDを表すドメインプリミティブ。"""

    def validate(self):
        """バリデーションルールを適用します。"""
        if not self.value or not self.value.strip():
            raise DomainValidationError("Userid cannot be empty")
        if len(self.value) > 50:
            raise DomainValidationError("Userid is too long")
        if not re.match(r"^[a-zA-Z0-9_-]+$", self.value):
            raise DomainValidationError("Userid contains invalid characters")


class Username(DomainPrimitive[str]):
    """ユーザー名を表すドメインプリミティブ。"""

    def validate(self):
        """バリデーションルールを適用します。"""
        if not self.value or not self.value.strip():
            raise DomainValidationError("Username cannot be empty")
        if len(self.value) > 50:
            raise DomainValidationError("Username is too long")


class MessageText(DomainPrimitive[str]):
    """メッセージ本文を表すドメインプリミティブ。"""

    def validate(self):
        """バリデーションルールを適用します。"""
        if not self.value or not self.value.strip():
            raise DomainValidationError("Message text cannot be empty")
        if len(self.value) > 1000:
            raise DomainValidationError("Message text is too long")


class TaskText(DomainPrimitive[str]):
    """タスク本文を表すドメインプリミティブ。"""

    def validate(self):
        """バリデーションルールを適用します。"""
        if not self.value or not self.value.strip():
            raise DomainValidationError("Task text cannot be empty")
        if len(self.value) > 500:
            raise DomainValidationError("Task text is too long")


class AuthToken(DomainPrimitive[str]):
    """認証用トークンを表すドメインプリミティブ。"""

    def validate(self):
        """バリデーションルールを適用します。"""
        if not self.value or not self.value.strip():
            raise DomainValidationError("Token cannot be empty")


class Password(DomainPrimitive[str]):
    """パスワードを表すドメインプリミティブ。"""

    def validate(self):
        """バリデーションルールを適用します。"""
        if not self.value:
            raise DomainValidationError("Password cannot be empty")
        if len(self.value) < 4:
            raise DomainValidationError("Password is too short")


class RefreshToken(DomainPrimitive[str]):
    """リフレッシュトークンを表すドメインプリミティブ。"""

    def validate(self):
        """バリデーションルールを適用します。"""
        if not self.value or not self.value.strip():
            raise DomainValidationError("RefreshToken cannot be empty")


class HashedPassword(DomainPrimitive[str]):
    """ハッシュ化されたパスワードを表すドメインプリミティブ。"""

    def validate(self):
        """バリデーションルールを適用します。"""
        if not self.value or not self.value.strip():
            raise DomainValidationError("HashedPassword cannot be empty")
        if not self.value.startswith(("$2a$", "$2b$", "$2y$")):
            raise DomainValidationError("HashedPassword must be a valid bcrypt hash")


class IpAddress(DomainPrimitive[str]):
    """IPアドレスを表すドメインプリミティブ。"""

    def validate(self):
        """バリデーションルールを適用します。"""
        if not self.value or not self.value.strip():
            raise DomainValidationError("IpAddress cannot be empty")
        try:
            ipaddress.ip_address(self.value)
        except ValueError:
            raise DomainValidationError("Invalid IP address format")


class UserAgent(DomainPrimitive[str]):
    """ユーザーエージェントを表すドメインプリミティブ。"""

    def validate(self):
        """バリデーションルールを適用します。"""
        if not self.value or not self.value.strip():
            raise DomainValidationError("UserAgent cannot be empty")
        if len(self.value) > 1000:
            raise DomainValidationError("UserAgent is too long (max 1000 characters)")


class SessionId(DomainPrimitive[uuid.UUID]):
    """セッションID（UUIDv7）を表すドメインプリミティブ。"""

    def validate(self):
        """バリデーションルールを適用します。"""
        if self.value.version != 7:
            raise DomainValidationError("SessionId must be a UUID v7")


class TokenHash(DomainPrimitive[str]):
    """トークンハッシュ値（SHA-256）を表すドメインプリミティブ。"""

    def validate(self):
        """バリデーションルールを適用します。"""
        if not self.value or not self.value.strip():
            raise DomainValidationError("TokenHash cannot be empty")
        if len(self.value) != 64:
            raise DomainValidationError("TokenHash must be exactly 64 characters long")
        if not re.match(r"^[0-9a-fA-F]+$", self.value):
            raise DomainValidationError("TokenHash must be a hexadecimal string")
