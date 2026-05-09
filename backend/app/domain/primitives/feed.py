"""配信イベント種別を表すドメインプリミティブ。"""

from enum import Enum


class FeedEventType(str, Enum):
    """ビジネスイベントの種類を表すドメインプリミティブ。"""

    __slots__ = ()
    MESSAGE = "message"
    REQUEST = "request"
    REQUEST_UPDATED = "request_updated"
    JOIN = "join"
    LEAVE = "leave"
