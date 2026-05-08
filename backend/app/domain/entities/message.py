"""チャットメッセージを表すドメインエンティティ。"""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.domain.primitives.primitives import EntityId, MessageText, Username

from .payload import MessagePayload


@dataclass(frozen=True, kw_only=True)
class DraftMessage:
    """新規メッセージ作成用のドメインエンティティ（Command 側）。

    アプリケーション層でメッセージを生成する際に使用します。
    永続化前のため id を持ちません。
    """

    username: Username  # メッセージを送信したユーザーの名前
    text: MessageText  # メッセージの本文
    # 作成日時。
    # リアルタイム通知の一貫性維持とドメイン層内での完結のため、アプリ側で生成します。
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, kw_only=True)
class Message(DraftMessage):
    """永続化済みチャットメッセージのドメインエンティティ（Query 側）。

    DB保存後にリポジトリから返されるエンティティです。
    id は必ず存在し、None チェックは不要です。
    """

    id: EntityId

    def to_payload(self) -> MessagePayload:
        """配信用 Payload に変換します。"""
        return MessagePayload(
            id=self.id,
            username=self.username,
            text=self.text,
            created_at=self.created_at,
        )
