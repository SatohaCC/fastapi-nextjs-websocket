"""配信フィードのルーティング戦略を定義するドメインサービス。"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ..entities.delivery_feed import DeliveryFeed

from ..primitives.feed import FeedEventType
from ..repositories.connection_manager import ConnectionManager

logger = logging.getLogger(__name__)


class FeedRoutingStrategy(Protocol):
    """イベントタイプに応じた配信戦略を定義するプロトコル。"""

    async def route(
        self,
        feed: DeliveryFeed,
        connection_manager: ConnectionManager,
    ) -> None:
        """フィードを適切な配信先に送信します。

        Args:
            feed: 配信するフィード。
            connection_manager: 接続管理サービス。
        """
        ...


class FeedRouter:
    """event_type に基づいて FeedRoutingStrategy を解決し、配信を委譲します。

    新しいイベントタイプの追加は register() を呼ぶだけで完了し、
    このクラス自体の変更は不要です（OCP 準拠）。
    """

    def __init__(self) -> None:
        """FeedRouter を初期化します。"""
        self._strategies: dict[FeedEventType, FeedRoutingStrategy] = {}

    def register(
        self,
        event_type: FeedEventType,
        strategy: FeedRoutingStrategy,
    ) -> None:
        """イベントタイプに対するルーティング戦略を登録します。

        Args:
            event_type: 対象のイベントタイプ。
            strategy: そのイベントに適用する配信戦略。
        """
        self._strategies[event_type] = strategy

    async def route(
        self,
        feed: DeliveryFeed,
        connection_manager: ConnectionManager,
    ) -> None:
        """フィードの event_type に応じた戦略を解決し、配信します。

        未登録の event_type の場合はログに警告を出力し、無視します。

        Args:
            feed: 配信するフィード。
            connection_manager: 接続管理サービス。
        """
        strategy = self._strategies.get(feed.event_type)
        if strategy is None:
            logger.warning(
                "No routing strategy registered for: %s",
                feed.event_type,
            )
            return

        await strategy.route(feed, connection_manager)
