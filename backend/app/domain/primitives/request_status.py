"""リクエストのステータスを表すドメインプリミティブ。"""

from enum import Enum


class RequestStatus(str, Enum):
    """リクエストの状態を表すドメインプリミティブ。
    Enumメンバは不変であり、__slots__ = () により属性の動的追加を禁止しています。
    """

    __slots__ = ()
    REQUESTED = "requested"
    PROCESSING = "processing"
    COMPLETED = "completed"

    def can_transition_to(self, next_status: "RequestStatus") -> bool:
        """指定されたステータスへの遷移が可能かどうかを判定します。
        ルール:
        - REQUESTED -> PROCESSING, COMPLETED
        - PROCESSING -> COMPLETED
        """
        if self == RequestStatus.REQUESTED:
            return next_status in (RequestStatus.PROCESSING, RequestStatus.COMPLETED)
        if self == RequestStatus.PROCESSING:
            return next_status == RequestStatus.COMPLETED
        return False
