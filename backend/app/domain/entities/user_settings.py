"""ユーザー通知設定を表すドメインエンティティ。"""

from dataclasses import dataclass

from app.domain.primitives.primitives import UserId


@dataclass(frozen=True, kw_only=True)
class UserSettings:
    """ユーザーの通知設定（グローバルチャット、ダイレクトリクエストなど）を表すエンティティ。"""

    user_id: UserId
    global_chat: bool
    direct_request: bool
    direct_request_updated: bool
    browser_notification: bool
