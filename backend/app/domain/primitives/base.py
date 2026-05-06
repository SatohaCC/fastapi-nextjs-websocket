"""ドメインプリミティブの基底クラス定義。"""

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class DomainPrimitive(Generic[T]):
    """ドメインプリミティブの基底クラス。
    不変性（frozen）と値による等価性を保証します。
    """

    value: T

    def __post_init__(self):
        """バリデーションが必要な場合は、継承先でオーバーライドします。"""
        self.validate()

    def validate(self):
        """ビジネスルールの検証ロジックを実装します。"""
        pass

    def __str__(self) -> str:
        """文字列としての表現を返します。"""
        return str(self.value)
