"""DirectRequest エンティティのステータス遷移・権限チェックのユニットテスト。"""

from datetime import datetime, timezone

import pytest

from app.domain.entities.direct_request import DirectRequest, DraftDirectRequest
from app.domain.exceptions import (
    DomainValidationError,
    InvalidOperationException,
    UnauthorizedException,
)
from app.domain.primitives.primitives import EntityId, RequestText, Username
from app.domain.primitives.request_status import RequestStatus


def make_request(
    sender: str = "alice",
    recipient: str = "bob",
    status: RequestStatus = RequestStatus.REQUESTED,
) -> DirectRequest:
    """テスト用 DirectRequest を生成するヘルパー。"""
    now = datetime.now(timezone.utc)
    return DirectRequest(
        id=EntityId(1),
        sender=Username(sender),
        recipient=Username(recipient),
        text=RequestText("please help"),
        status=status,
        created_at=now,
        updated_at=now,
    )


class TestDraftDirectRequest:
    """DraftDirectRequest の不変条件テスト。"""

    def test_self_request_raises(self):
        """送信者と受信者が同じ場合は DomainValidationError を送出する。"""
        with pytest.raises(DomainValidationError):
            DraftDirectRequest(
                sender=Username("alice"),
                recipient=Username("alice"),
                text=RequestText("test"),
                status=RequestStatus.REQUESTED,
            )

    def test_different_sender_recipient_is_valid(self):
        """送信者と受信者が異なる場合は有効。"""
        DraftDirectRequest(
            sender=Username("alice"),
            recipient=Username("bob"),
            text=RequestText("test"),
            status=RequestStatus.REQUESTED,
        )


class TestDirectRequestTransition:
    """DirectRequest.transition_to のテスト。"""

    def test_valid_transition_updates_status(self):
        """受信者による有効な遷移でステータスが更新される。"""
        req = make_request()
        updated = req.transition_to(RequestStatus.PROCESSING, Username("bob"))
        assert updated.status == RequestStatus.PROCESSING

    def test_valid_transition_updates_timestamp(self):
        """有効な遷移後に updated_at が更新される（元の値以上）。"""
        req = make_request()
        updated = req.transition_to(RequestStatus.PROCESSING, Username("bob"))
        assert updated.updated_at >= req.updated_at

    def test_non_recipient_raises_unauthorized(self):
        """受信者以外が操作すると UnauthorizedException を送出する。"""
        req = make_request()
        with pytest.raises(UnauthorizedException):
            req.transition_to(RequestStatus.PROCESSING, Username("alice"))

    def test_invalid_transition_raises(self):
        """無効なステータス遷移は InvalidOperationException を送出する。"""
        req = make_request(status=RequestStatus.COMPLETED)
        with pytest.raises(InvalidOperationException):
            req.transition_to(RequestStatus.REQUESTED, Username("bob"))

    def test_chained_valid_transitions(self):
        """REQUESTED → PROCESSING → COMPLETED の連続遷移が成功する。"""
        req = make_request()
        processing = req.transition_to(RequestStatus.PROCESSING, Username("bob"))
        completed = processing.transition_to(RequestStatus.COMPLETED, Username("bob"))
        assert completed.status == RequestStatus.COMPLETED

    def test_transition_returns_new_instance(self):
        """transition_to は元のインスタンスを変更せず新しいインスタンスを返す。

        不変性の検証。
        """
        req = make_request()
        updated = req.transition_to(RequestStatus.PROCESSING, Username("bob"))
        assert req.status == RequestStatus.REQUESTED
        assert updated.status == RequestStatus.PROCESSING
        assert req is not updated
