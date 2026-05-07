"""ドメインプリミティブのバリデーションと RequestStatus 遷移のユニットテスト。"""

import pytest

from app.domain.exceptions import DomainValidationError
from app.domain.primitives.primitives import (
    AuthToken,
    EntityId,
    MessageText,
    Password,
    RequestText,
    Username,
)
from app.domain.primitives.request_status import RequestStatus


class TestEntityId:
    """EntityId のバリデーションテスト。"""

    def test_zero_is_valid(self):
        """0 は有効な EntityId。"""
        assert EntityId(0).value == 0

    def test_positive_is_valid(self):
        """正の整数は有効な EntityId。"""
        assert EntityId(42).value == 42

    def test_negative_raises(self):
        """負の値は DomainValidationError を送出する。"""
        with pytest.raises(DomainValidationError):
            EntityId(-1)


class TestUsername:
    """Username のバリデーションテスト。"""

    def test_valid(self):
        """通常のユーザー名は有効。"""
        assert Username("alice").value == "alice"

    def test_empty_raises(self):
        """空文字列は DomainValidationError を送出する。"""
        with pytest.raises(DomainValidationError):
            Username("")

    def test_whitespace_only_raises(self):
        """空白のみの文字列は DomainValidationError を送出する。"""
        with pytest.raises(DomainValidationError):
            Username("   ")

    def test_too_long_raises(self):
        """51文字以上は DomainValidationError を送出する。"""
        with pytest.raises(DomainValidationError):
            Username("a" * 51)

    def test_max_length_is_valid(self):
        """50文字ちょうどは有効（境界値）。"""
        Username("a" * 50)


class TestMessageText:
    """MessageText のバリデーションテスト。"""

    def test_valid(self):
        """通常のメッセージは有効。"""
        assert MessageText("hello").value == "hello"

    def test_empty_raises(self):
        """空文字列は DomainValidationError を送出する。"""
        with pytest.raises(DomainValidationError):
            MessageText("")

    def test_whitespace_only_raises(self):
        """空白のみは DomainValidationError を送出する。"""
        with pytest.raises(DomainValidationError):
            MessageText("   ")

    def test_too_long_raises(self):
        """1001文字以上は DomainValidationError を送出する。"""
        with pytest.raises(DomainValidationError):
            MessageText("a" * 1001)

    def test_max_length_is_valid(self):
        """1000文字ちょうどは有効（境界値）。"""
        MessageText("a" * 1000)


class TestRequestText:
    """RequestText のバリデーションテスト。"""

    def test_valid(self):
        """通常のリクエスト本文は有効。"""
        assert RequestText("please do this").value == "please do this"

    def test_empty_raises(self):
        """空文字列は DomainValidationError を送出する。"""
        with pytest.raises(DomainValidationError):
            RequestText("")

    def test_too_long_raises(self):
        """501文字以上は DomainValidationError を送出する。"""
        with pytest.raises(DomainValidationError):
            RequestText("a" * 501)

    def test_max_length_is_valid(self):
        """500文字ちょうどは有効（境界値）。"""
        RequestText("a" * 500)


class TestAuthToken:
    """AuthToken のバリデーションテスト。"""

    def test_valid(self):
        """通常のトークン文字列は有効。"""
        token = AuthToken("some.jwt.token")
        assert token.value == "some.jwt.token"

    def test_empty_raises(self):
        """空文字列は DomainValidationError を送出する。"""
        with pytest.raises(DomainValidationError):
            AuthToken("")

    def test_whitespace_only_raises(self):
        """空白のみは DomainValidationError を送出する。"""
        with pytest.raises(DomainValidationError):
            AuthToken("   ")


class TestPassword:
    """Password のバリデーションテスト。"""

    def test_valid(self):
        """4文字以上のパスワードは有効。"""
        assert Password("pass").value == "pass"

    def test_empty_raises(self):
        """空文字列は DomainValidationError を送出する。"""
        with pytest.raises(DomainValidationError):
            Password("")

    def test_too_short_raises(self):
        """3文字以下は DomainValidationError を送出する。"""
        with pytest.raises(DomainValidationError):
            Password("abc")

    def test_min_length_is_valid(self):
        """4文字ちょうどは有効（境界値）。"""
        Password("abcd")


class TestRequestStatusTransitions:
    """RequestStatus のステータス遷移ルールテスト。"""

    def test_requested_to_processing_is_valid(self):
        """REQUESTED → PROCESSING は有効な遷移。"""
        assert RequestStatus.REQUESTED.can_transition_to(RequestStatus.PROCESSING)

    def test_requested_to_completed_is_valid(self):
        """REQUESTED → COMPLETED は有効な遷移。"""
        assert RequestStatus.REQUESTED.can_transition_to(RequestStatus.COMPLETED)

    def test_processing_to_completed_is_valid(self):
        """PROCESSING → COMPLETED は有効な遷移。"""
        assert RequestStatus.PROCESSING.can_transition_to(RequestStatus.COMPLETED)

    def test_completed_to_requested_is_invalid(self):
        """COMPLETED → REQUESTED は無効な遷移（完了済みに戻れない）。"""
        assert not RequestStatus.COMPLETED.can_transition_to(RequestStatus.REQUESTED)

    def test_completed_to_processing_is_invalid(self):
        """COMPLETED → PROCESSING は無効な遷移。"""
        assert not RequestStatus.COMPLETED.can_transition_to(RequestStatus.PROCESSING)

    def test_processing_to_requested_is_invalid(self):
        """PROCESSING → REQUESTED は無効な遷移。"""
        assert not RequestStatus.PROCESSING.can_transition_to(RequestStatus.REQUESTED)
