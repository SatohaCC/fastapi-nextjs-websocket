"""パスワード検証サービスを抽象化するアプリケーション層インターフェース。"""

from typing import Protocol


class PasswordVerifier(Protocol):
    """パスワード検証の抽象インタフェース。"""

    def verify(self, plain: str, hashed: str) -> bool:
        """平文パスワードとハッシュ化されたパスワードを検証します。

        Args:
            plain: 平文のパスワード。
            hashed: ハッシュ化されたパスワード。

        Returns:
            検証結果（一致していれば True、不一致なら False）。
        """
        ...

    def hash(self, plain: str) -> str:
        """平文パスワードをハッシュ化します。

        Args:
            plain: 平文のパスワード。

        Returns:
            ハッシュ化されたパスワード。
        """
        ...
