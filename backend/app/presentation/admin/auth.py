"""SQLAdmin 用の管理画面認証バックエンド実装。"""

from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from sqladmin.authentication import AuthenticationBackend

from ...infrastructure.config import settings


class AdminAuth(AuthenticationBackend):
    """SQLAdmin 用の認証バックエンドクラス。

    環境変数に設定された ADMIN_USERNAME / ADMIN_PASSWORD を使用して
    簡易的に認証を行います。
    """

    async def login(self, request: Request) -> bool:
        """ログイン画面のフォームデータを検証し、セッションにログイン状態を記録します。"""
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        # 環境変数の認証情報と照合
        if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
            request.session.update({"token": "admin-logged-in"})
            return True

        return False

    async def logout(self, request: Request) -> bool:
        """管理セッションをクリアしてログアウトします。"""
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> RedirectResponse | bool:
        """リクエスト元のセッションを検証し、未ログインの場合はログイン画面へリダイレクトします。"""
        token = request.session.get("token")

        if not token:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        return True


# 認証バックエンドのインスタンスを生成 (セッション署名用の秘密鍵を指定)
admin_auth = AdminAuth(secret_key=settings.ADMIN_SECRET_KEY)
