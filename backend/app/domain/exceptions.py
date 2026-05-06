"""ドメイン層のビジネスルール違反を表す例外クラス群。"""


class DomainException(Exception):
    """ドメイン層の基本例外クラス"""


class EntityNotFoundException(DomainException):
    """エンティティが見つからない場合の例外"""


class UnauthorizedException(DomainException):
    """操作権限がない場合の例外"""


class InvalidOperationException(DomainException):
    """不正な操作（例：自分自身へのリクエストなど）の例外"""


class DomainValidationError(DomainException):
    """バリデーションエラー（ドメインプリミティブの制約違反など）の例外"""
