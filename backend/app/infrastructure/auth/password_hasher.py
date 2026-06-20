"""bcrypt を使用したパスワードのハッシュ化および検証ユーティリティ。"""

import bcrypt

from app.application.interfaces.password import PasswordVerifier


class PasswordHasher(PasswordVerifier):
    """パスワードのセキュアなハッシュ化と照合を行うクラス。"""

    def verify(self, plain: str, hashed: str) -> bool:
        """平文パスワードとハッシュ値を照合します。"""
        try:
            return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
        except ValueError:
            return False

    def hash(self, plain: str) -> str:
        """平文パスワードをハッシュ化します。"""
        return self.hash_password(plain)

    @staticmethod
    def hash_password(password: str) -> str:
        """生のパスワード文字列をハッシュ化して返します。"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
