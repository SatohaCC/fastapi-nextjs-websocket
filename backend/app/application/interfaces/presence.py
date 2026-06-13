"""クラスタ全体の在席（presence）ストアのインターフェース定義。"""

from typing import Protocol


class PresenceStore(Protocol):
    """複数バックエンドインスタンス間で共有する在席ストアのインターフェース。

    在席ロスターと JOIN/LEAVE の判定をプロセスローカルではなく共有ストア
    （Redis 等）で行うことで、スケールアウト時に在席が分裂しないようにする。
    接続は参照カウントで管理し、同一ユーザーが複数タブ・複数インスタンスに
    跨って接続していても 1 ユーザーとして扱う。

    各接続は一意な ``conn_id`` で識別し、有効期限（TTL）付きで登録する。
    生存中の接続は ``refresh_connection`` で定期的に期限を延長する。期限切れの
    エントリは読み書き時に掃除（reap）されるため、非グレースフルなクラッシュで
    ``remove_connection`` が呼ばれなかった接続も TTL 経過後に自動的に消える。
    """

    async def add_connection(self, username: str, conn_id: str) -> bool:
        """接続を 1 つ追加します。

        Args:
            username: 接続するユーザー名。
            conn_id: この接続を一意に識別する ID。

        Returns:
            このユーザーがクラスタ全体で初めてオンラインになった（0→1）場合 True。
            呼び出し側はこれを JOIN 配信の要否判定に使う。
        """
        ...

    async def remove_connection(self, username: str, conn_id: str) -> bool:
        """接続を 1 つ削除します。

        Args:
            username: 切断するユーザー名。
            conn_id: 削除する接続の ID。

        Returns:
            このユーザーのクラスタ全体で最後の接続が切れた（→0）場合 True。
            呼び出し側はこれを LEAVE 配信の要否判定に使う。
        """
        ...

    async def refresh_connection(self, username: str, conn_id: str) -> None:
        """接続の有効期限を延長します（生存通知）。

        生存中の接続から定期的に呼び出し、TTL 経過による誤った期限切れを防ぐ。

        Args:
            username: 対象ユーザー名。
            conn_id: 延長する接続の ID。
        """
        ...

    async def online_usernames(self) -> list[str]:
        """現在オンラインのユーザー名一覧（ソート済み）を返します。"""
        ...
