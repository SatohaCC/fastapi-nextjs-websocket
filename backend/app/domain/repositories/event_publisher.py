"""イベントのパブリッシュを抽象化するリポジトリインターフェース。"""

from typing import Protocol


class EventPublisher(Protocol):  # pylint: disable=too-few-public-methods
    """イベントのパブリッシュ（配信）を担当するインターフェース。
    Redis などの外部メッセージブローカーを介してシステム全体にイベントを通知します。
    """

    async def publish(self, event: dict) -> None:
        """指定されたイベントデータをパブリッシュします。

        Args:
            event (dict): 配信するイベントデータ。type フィールドを含む必要があります。
        """
        ...
