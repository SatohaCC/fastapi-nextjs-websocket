"""Outbox パターンのための DeliveryFeed エンティティ。"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, kw_only=True)
class DeliveryFeed:
    """Outbox に記録される配信フィードデータ。"""

    sequence_name: str | None = None
    sequence_id: int | None = None
    event_type: str  # "message" / "request" / "request_updated"
    payload: dict  # Redis publish 用ペイロード（seq は relay 時に付与）
    status: str = "PENDING"
    created_at: datetime
