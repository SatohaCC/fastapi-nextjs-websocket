"""ダイレクト・リクエストを管理するドメインエンティティ。"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone

from app.domain.exceptions import (
    DomainValidationError,
    InvalidOperationException,
    UnauthorizedException,
)
from app.domain.primitives.primitives import EntityId, RequestText, Username
from app.domain.primitives.request_status import RequestStatus


@dataclass(frozen=True, kw_only=True)
class DirectRequest:
    """ユーザー間のダイレクト・リクエストを表すドメインエンティティ。"""

    # 永続化（DB保存）前にアプリケーション層でエンティティを生成・検証できるよう、
    # 発番前のIDをNoneで許容します。
    id: EntityId | None = None
    sender: Username  # 送信者
    recipient: Username  # 受信者
    text: RequestText
    status: RequestStatus
    # 作成・更新日時はドメイン層内での一貫性維持、リアルタイム通知の低遅延化、
    # およびテスト容易性の向上のため、アプリ側で生成します。
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        """バリデーションルールを適用します。"""
        if self.sender == self.recipient:
            raise DomainValidationError("Sender and recipient cannot be the same")

    def transition_to(
        self, next_status: RequestStatus, operator: Username
    ) -> DirectRequest:
        """ステータスを次の状態へ遷移させた新しいインスタンスを返します。
        バリデーションを行い、成功した場合は updated_at も更新します。
        """
        # 権限チェック: 受信者本人以外はステータスを変更できない
        if self.recipient != operator:
            raise UnauthorizedException("Only the recipient can update the status")

        self.validate_status_transition(next_status)
        return replace(
            self,
            status=next_status,
            updated_at=datetime.now(timezone.utc),
        )

    def validate_status_transition(self, next_status: RequestStatus) -> None:
        """ステータス遷移の妥当性を検証します。
        不正な遷移の場合は InvalidOperationException を送出します。
        """
        if not self.status.can_transition_to(next_status):
            raise InvalidOperationException(
                f"Invalid status transition: {self.status.value} -> {next_status.value}"
            )
