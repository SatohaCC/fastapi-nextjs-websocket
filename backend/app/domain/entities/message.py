"""チャットメッセージを表すドメインエンティティ。"""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.domain.primitives.primitives import EntityId, MessageText, Username


@dataclass(frozen=True, kw_only=True)
class Message:
    """チャットメッセージを表すドメインエンティティ。
    グローバルチャットでやり取りされるメッセージの不変なデータを保持します。
    """

    # 永続化（DB保存）前にアプリケーション層でエンティティを生成できるよう、
    # 発番前のIDをNoneで許容します。
    id: EntityId | None = None
    username: Username  # メッセージを送信したユーザーの名前
    text: MessageText  # メッセージの本文
    # 作成日時。
    # リアルタイム通知の一貫性維持とドメイン層内での完結のため、アプリ側で生成します。
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
