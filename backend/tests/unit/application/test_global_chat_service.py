"""GlobalChatService のユニットテスト（UoW / Repository をモック化）。"""

from datetime import datetime, timezone

import pytest

from app.application.outbox.delivery_feed import GLOBAL_CHAT_SEQUENCE
from app.application.outbox.payload import GlobalChatPayload
from app.application.services.global_chat_service import GlobalChatService
from app.domain.entities.message import Message
from app.domain.primitives.primitives import EntityId, MessageText, Username


@pytest.fixture
def saved_message() -> Message:
    """テスト用の永続化済み Message。"""
    return Message(
        id=EntityId(1),
        username=Username("alice"),
        text=MessageText("hello"),
        created_at=datetime.now(timezone.utc),
    )


class TestGlobalChatServiceSendMessage:
    """GlobalChatService.send_message のテスト。"""

    async def test_saves_message_to_repository(self, mock_uow, saved_message):
        """messages.save が 1 回呼ばれること。"""
        mock_uow.messages.save.return_value = saved_message
        service = GlobalChatService(mock_uow)
        await service.send_message(Username("alice"), MessageText("hello"))
        mock_uow.messages.save.assert_called_once()

    async def test_saves_feed_to_outbox(self, mock_uow, saved_message):
        """outbox.save が 1 回呼ばれること（Transactional Outbox）。"""
        mock_uow.messages.save.return_value = saved_message
        service = GlobalChatService(mock_uow)
        await service.send_message(Username("alice"), MessageText("hello"))
        mock_uow.outbox.save.assert_called_once()

    async def test_commits_transaction(self, mock_uow, saved_message):
        """Commit が 1 回呼ばれること。"""
        mock_uow.messages.save.return_value = saved_message
        service = GlobalChatService(mock_uow)
        await service.send_message(Username("alice"), MessageText("hello"))
        mock_uow.commit.assert_called_once()

    async def test_returns_saved_message(self, mock_uow, saved_message):
        """messages.save の戻り値がそのまま返ること。"""
        mock_uow.messages.save.return_value = saved_message
        service = GlobalChatService(mock_uow)
        result = await service.send_message(Username("alice"), MessageText("hello"))
        assert result == saved_message

    async def test_draft_message_contains_correct_fields(self, mock_uow, saved_message):
        """messages.save に渡された DraftMessage のフィールドが正しいこと。"""
        mock_uow.messages.save.return_value = saved_message
        service = GlobalChatService(mock_uow)
        await service.send_message(Username("alice"), MessageText("hello"))

        call_args = mock_uow.messages.save.call_args
        draft = call_args.args[0]
        assert draft.username == Username("alice")
        assert draft.text == MessageText("hello")

    async def test_outbox_feed_payload_maps_entity_fields(
        self, mock_uow, saved_message
    ):
        """Outbox の GlobalChatPayload が entity のフィールドと一致すること。"""
        mock_uow.messages.save.return_value = saved_message
        service = GlobalChatService(mock_uow)
        await service.send_message(Username("alice"), MessageText("hello"))

        feed = mock_uow.outbox.save.call_args.args[0]
        assert isinstance(feed.payload, GlobalChatPayload)
        assert feed.payload.id == saved_message.id
        assert feed.payload.username == saved_message.username
        assert feed.payload.text == saved_message.text
        assert feed.payload.created_at == saved_message.created_at

    async def test_outbox_feed_uses_global_chat_sequence(self, mock_uow, saved_message):
        """Outbox フィードのシーケンス名が GLOBAL_CHAT_SEQUENCE であること。"""
        mock_uow.messages.save.return_value = saved_message
        service = GlobalChatService(mock_uow)
        await service.send_message(Username("alice"), MessageText("hello"))

        feed = mock_uow.outbox.save.call_args.args[0]
        assert feed.sequence_name == GLOBAL_CHAT_SEQUENCE


class TestGlobalChatServiceGetMessages:
    """GlobalChatService.get_messages_after / get_recent_messages のテスト。"""

    async def test_get_messages_after_delegates_to_repository(self, mock_uow):
        """get_messages_after が messages.get_after を正しい引数で呼ぶこと。"""
        mock_uow.messages.get_after.return_value = []
        service = GlobalChatService(mock_uow)
        result = await service.get_messages_after(EntityId(5))
        mock_uow.messages.get_after.assert_called_once_with(EntityId(5))
        assert result == []

    async def test_get_recent_messages_uses_default_limit(self, mock_uow):
        """デフォルト limit=50 で messages.get_recent を呼ぶこと。"""
        mock_uow.messages.get_recent.return_value = []
        service = GlobalChatService(mock_uow)
        await service.get_recent_messages()
        mock_uow.messages.get_recent.assert_called_once_with(50)

    async def test_get_recent_messages_accepts_custom_limit(self, mock_uow):
        """get_recent_messages がカスタム limit を渡すこと。"""
        mock_uow.messages.get_recent.return_value = []
        service = GlobalChatService(mock_uow)
        await service.get_recent_messages(limit=10)
        mock_uow.messages.get_recent.assert_called_once_with(10)
