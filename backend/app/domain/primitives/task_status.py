"""タスクのステータスを表すドメインプリミティブ。"""

from enum import Enum


class TaskStatus(str, Enum):
    """タスクの状態を表すドメインプリミティブ。
    Enumメンバは不変であり、__slots__ = () により属性の動的追加を禁止しています。
    """

    __slots__ = ()
    REQUESTED = "requested"
    PROCESSING = "processing"
    COMPLETED = "completed"

    def can_transition_to(self, next_status: "TaskStatus") -> bool:
        """指定されたステータスへの遷移が可能かどうかを判定します。
        ルール:
        - REQUESTED -> PROCESSING, COMPLETED
        - PROCESSING -> COMPLETED
        """
        if self == TaskStatus.REQUESTED:
            return next_status in (TaskStatus.PROCESSING, TaskStatus.COMPLETED)
        if self == TaskStatus.PROCESSING:
            return next_status == TaskStatus.COMPLETED
        return False
