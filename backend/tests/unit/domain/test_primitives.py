"""ドメインプリミティブのバリデーションと TaskStatus 遷移のユニットテスト。"""

import pytest

from app.domain.exceptions import DomainValidationError
from app.domain.primitives.primitives import (
    AuthToken,
    EntityId,
    MessageText,
    Password,
    TaskText,
    Username,
)
from app.domain.primitives.task_status import TaskStatus


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


class TestTaskText:
    """TaskText のバリデーションテスト。"""

    def test_valid(self):
        """通常の Task 本文は有効。"""
        assert TaskText("please do this").value == "please do this"

    def test_empty_raises(self):
        """空文字列は DomainValidationError を送出する。"""
        with pytest.raises(DomainValidationError):
            TaskText("")

    def test_too_long_raises(self):
        """501文字以上は DomainValidationError を送出する。"""
        with pytest.raises(DomainValidationError):
            TaskText("a" * 501)

    def test_max_length_is_valid(self):
        """500文字ちょうどは有効（境界値）。"""
        TaskText("a" * 500)


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


class TestTaskStatusTransitions:
    """TaskStatus のステータス遷移ルールテスト。"""

    def test_requested_to_processing_is_valid(self):
        """REQUESTED → PROCESSING は有効な遷移。"""
        assert TaskStatus.REQUESTED.can_transition_to(TaskStatus.PROCESSING)

    def test_requested_to_completed_is_valid(self):
        """REQUESTED → COMPLETED は有効な遷移。"""
        assert TaskStatus.REQUESTED.can_transition_to(TaskStatus.COMPLETED)

    def test_processing_to_completed_is_valid(self):
        """PROCESSING → COMPLETED は有効な遷移。"""
        assert TaskStatus.PROCESSING.can_transition_to(TaskStatus.COMPLETED)

    def test_completed_to_requested_is_invalid(self):
        """COMPLETED → REQUESTED は無効な遷移（完了済みに戻れない）。"""
        assert not TaskStatus.COMPLETED.can_transition_to(TaskStatus.REQUESTED)

    def test_completed_to_processing_is_invalid(self):
        """COMPLETED → PROCESSING は無効な遷移。"""
        assert not TaskStatus.COMPLETED.can_transition_to(TaskStatus.PROCESSING)

    def test_processing_to_requested_is_invalid(self):
        """PROCESSING → REQUESTED は無効な遷移。"""
        assert not TaskStatus.PROCESSING.can_transition_to(TaskStatus.REQUESTED)
