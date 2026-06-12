"""DirectStrategy のユニットテスト（ConnectionManager をモック化）。

per-user inbox 化により、各 feed は ``direct_request:{username}`` という単一
ユーザー宛のシーケンス名を持つ。DirectStrategy はその所有者 1 人にだけ配信し、
もう一方には送らないことを検証する。
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.application.outbox.delivery_feed import (
    DeliveryFeed,
    SequenceId,
    direct_request_sequence,
)
from app.application.outbox.payload import DirectRequestPayload
from app.application.services.routing_strategies import DirectStrategy
from app.domain.primitives.primitives import EntityId, TaskText, UserId, Username
from app.domain.primitives.task_status import TaskStatus

ALICE_ID = UserId(uuid.uuid7())
BOB_ID = UserId(uuid.uuid7())


def _dm_feed(owner: str) -> DeliveryFeed:
    """alice→bob の DM を、``owner`` の inbox 用 feed として組み立てる。"""
    now = datetime.now(timezone.utc)
    payload = DirectRequestPayload(
        id=EntityId(1),
        sender_id=ALICE_ID,
        recipient_id=BOB_ID,
        sender=Username("alice"),
        recipient=Username("bob"),
        text=TaskText("please review"),
        status=TaskStatus.REQUESTED,
        created_at=now,
        updated_at=now,
    )
    return DeliveryFeed(
        sequence_name=direct_request_sequence(owner),
        event_type=payload.event_type,
        payload=payload,
        sequence_id=SequenceId(1),
    )


@pytest.mark.asyncio
async def test_routes_to_recipient_inbox_owner_only() -> None:
    """recipient(bob) の inbox feed は bob にのみ届き、alice には送らない。"""
    cm = AsyncMock()
    await DirectStrategy().route(_dm_feed("bob"), cm)
    cm.send_to_user.assert_awaited_once()
    assert cm.send_to_user.await_args.args[0] == BOB_ID


@pytest.mark.asyncio
async def test_routes_to_sender_inbox_owner_only() -> None:
    """sender(alice) の inbox feed は alice にのみ届く。"""
    cm = AsyncMock()
    await DirectStrategy().route(_dm_feed("alice"), cm)
    cm.send_to_user.assert_awaited_once()
    assert cm.send_to_user.await_args.args[0] == ALICE_ID


@pytest.mark.asyncio
async def test_unrelated_inbox_owner_not_delivered() -> None:
    """sender/recipient のどちらでもない所有者には配信しない（防御的）。"""
    cm = AsyncMock()
    await DirectStrategy().route(_dm_feed("charlie"), cm)
    cm.send_to_user.assert_not_awaited()
