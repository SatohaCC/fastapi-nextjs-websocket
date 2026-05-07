"""配信フィードに関連するドメインプリミティブの定義。"""

from enum import Enum

from ..exceptions import DomainValidationError
from .base import DomainPrimitive


class SequenceName(DomainPrimitive[str]):
    """配信シーケンス名を表すドメインプリミティブ。"""

    def validate(self):
        """シーケンス名のバリデーション。"""
        if not self.value or not self.value.strip():
            raise DomainValidationError("Sequence name cannot be empty")


class SequenceId(DomainPrimitive[int]):
    """配信シーケンスIDを表すドメインプリミティブ。"""

    def validate(self):
        """シーケンスIDのバリデーション。"""
        if self.value < 0:
            raise DomainValidationError("Sequence ID must be non-negative")


class FeedEventType(str, Enum):
    """配信イベントの種類を表すドメインプリミティブ。"""

    __slots__ = ()
    MESSAGE = "message"
    REQUEST = "request"
    REQUEST_UPDATED = "request_updated"


class FeedStatus(str, Enum):
    """配信状態を表すドメインプリミティブ。"""

    __slots__ = ()
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
