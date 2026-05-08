"""システムイベントを表すドメインエンティティ。"""

from dataclasses import dataclass

from app.domain.primitives.feed import FeedEventType
from app.domain.primitives.primitives import Username

from .payload import SystemEventPayload


@dataclass(frozen=True)
class SystemEvent:
    """入退室などのシステムレベルのイベントを表すエンティティ。"""

    type: FeedEventType
    username: Username

    def to_payload(self) -> SystemEventPayload:
        """配信用 Payload に変換します。"""
        return SystemEventPayload(
            type=self.type,
            username=self.username,
        )
