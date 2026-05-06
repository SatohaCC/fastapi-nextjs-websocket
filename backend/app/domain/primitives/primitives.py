"""アプリケーションで使用するドメインプリミティブの定義。"""

from ..exceptions import DomainValidationError
from .base import DomainPrimitive


class EntityId(DomainPrimitive[int]):
    """エンティティの一意識別子。"""

    def validate(self):
        """バリデーションルールを適用します。"""
        if self.value < 0:
            raise DomainValidationError("EntityId must be non-negative")


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


class RequestText(DomainPrimitive[str]):
    """リクエスト本文を表すドメインプリミティブ。"""

    def validate(self):
        """バリデーションルールを適用します。"""
        if not self.value or not self.value.strip():
            raise DomainValidationError("Request text cannot be empty")
        if len(self.value) > 500:
            raise DomainValidationError("Request text is too long")
