"""bcrypt を使用したパスワードのハッシュ化および検証ユーティリティ。"""

import bcrypt


class PasswordHasher:
    """パスワードのセキュアなハッシュ化と照合を行うクラス。"""

    @staticmethod
    def hash_password(password: str) -> str:
        """生のパスワード文字列をハッシュ化して返します。"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """生のパスワードとハッシュ値を照合し、一致するか確認します。"""
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"), hashed_password.encode("utf-8")
            )
        except Exception:
            return False
