"""SQLAdmin 用のデータベースモデルビュー定義。"""

from sqladmin import ModelView
from sqladmin.filters import AllUniqueStringValuesFilter, OperationColumnFilter

from ...infrastructure.persistence.orm_models import (
    DeliveryFeedORM,
    DeliverySequenceORM,
    MessageORM,
    RefreshTokenORM,
    TaskORM,
    UserORM,
    UserSettingsORM,
)


class UserAdmin(ModelView, model=UserORM):
    """ユーザーモデルの管理画面定義。"""

    name = "ユーザー"
    name_plural = "ユーザー一覧"
    icon = "fa-solid fa-user"
    column_list = [UserORM.id, UserORM.username, UserORM.created_at]
    column_searchable_list = [UserORM.username]
    # セキュリティのためハッシュ化パスワードは表示・編集させない
    column_details_exclude_list = ["hashed_password"]  # type: ignore[list-item]
    form_excluded_columns = ["hashed_password"]  # type: ignore[list-item]


class MessageAdmin(ModelView, model=MessageORM):
    """チャットメッセージモデル of 管理画面定義。"""

    name = "メッセージ"
    name_plural = "メッセージ一覧"
    icon = "fa-solid fa-message"
    column_list = [
        MessageORM.id,
        MessageORM.username,
        MessageORM.text,
        MessageORM.created_at,
    ]
    column_searchable_list = [MessageORM.username, MessageORM.text]
    column_filters = [
        AllUniqueStringValuesFilter(MessageORM.username, title="ユーザー名"),
    ]


class TaskAdmin(ModelView, model=TaskORM):
    """ダイレクトリクエストモデルの管理画面定義。"""

    name = "タスク"
    name_plural = "タスク一覧"
    icon = "fa-solid fa-list-check"
    column_list = [
        TaskORM.id,
        TaskORM.sender,
        TaskORM.recipient,
        TaskORM.text,
        TaskORM.status,
        TaskORM.created_at,
    ]
    column_searchable_list = [TaskORM.sender, TaskORM.recipient, TaskORM.text]
    column_filters = [
        AllUniqueStringValuesFilter(TaskORM.status, title="ステータス"),
        AllUniqueStringValuesFilter(TaskORM.sender, title="送信者"),
        AllUniqueStringValuesFilter(TaskORM.recipient, title="受信者"),
    ]


class UserSettingsAdmin(ModelView, model=UserSettingsORM):
    """ユーザー設定モデルの管理画面定義。"""

    name = "通知設定"
    name_plural = "通知設定一覧"
    icon = "fa-solid fa-gear"
    column_list = [
        UserSettingsORM.user_id,
        UserSettingsORM.global_chat,
        UserSettingsORM.direct_request,
        UserSettingsORM.direct_request_updated,
        UserSettingsORM.updated_at,
    ]
    column_filters = []


class RefreshTokenAdmin(ModelView, model=RefreshTokenORM):
    """リフレッシュトークンモデルの管理画面定義。"""

    name = "セッショントークン"
    name_plural = "セッショントークン一覧"
    icon = "fa-solid fa-key"
    column_list = [
        RefreshTokenORM.id,
        RefreshTokenORM.user_id,
        RefreshTokenORM.expires_at,
        RefreshTokenORM.created_at,
        RefreshTokenORM.ip_address,
    ]
    column_details_exclude_list = ["token_hash"]  # type: ignore[list-item]
    form_excluded_columns = ["token_hash"]  # type: ignore[list-item]
    column_filters = [
        OperationColumnFilter(RefreshTokenORM.user_id, title="ユーザーID"),
    ]


class DeliverySequenceAdmin(ModelView, model=DeliverySequenceORM):
    """配信シーケンスモデルの管理画面定義。"""

    name = "配信シーケンス"
    name_plural = "配信シーケンス一覧"
    icon = "fa-solid fa-arrow-down-1-9"
    column_list = [DeliverySequenceORM.name, DeliverySequenceORM.last_id]


class DeliveryFeedAdmin(ModelView, model=DeliveryFeedORM):
    """Outbox配信ログモデルの管理画面定義。"""

    name = "配信フィード"
    name_plural = "配信フィード一覧"
    icon = "fa-solid fa-envelope-open"
    column_list = [
        DeliveryFeedORM.sequence_name,
        DeliveryFeedORM.sequence_id,
        DeliveryFeedORM.event_type,
        DeliveryFeedORM.status,
        DeliveryFeedORM.created_at,
    ]
    column_filters = [
        AllUniqueStringValuesFilter(
            DeliveryFeedORM.sequence_name, title="シーケンス名"
        ),
        AllUniqueStringValuesFilter(DeliveryFeedORM.status, title="ステータス"),
        AllUniqueStringValuesFilter(DeliveryFeedORM.event_type, title="イベント種別"),
    ]


# すべての管理画面ビューをリストとしてエクスポート
all_views = [
    UserAdmin,
    MessageAdmin,
    TaskAdmin,
    UserSettingsAdmin,
    RefreshTokenAdmin,
    DeliverySequenceAdmin,
    DeliveryFeedAdmin,
]
