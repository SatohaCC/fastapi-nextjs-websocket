"""SQLAdmin 管理画面の結合テスト。"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.infrastructure.config import settings
from app.main import app


@pytest.mark.anyio
async def test_admin_portal_redirects_unauthenticated():
    """未認証で /admin にアクセスした際、ログイン画面へリダイレクトされることを確認。"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # リダイレクトを追跡しない設定
        response = await client.get("/admin/")
        assert response.status_code == 302
        assert "/admin/login" in response.headers.get("location", "")


@pytest.mark.anyio
async def test_admin_portal_login_success():
    """正しい認証情報でログインし、ダッシュボードにアクセスできることを確認。"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # ログイン試行
        login_data = {
            "username": settings.ADMIN_USERNAME,
            "password": settings.ADMIN_PASSWORD,
        }
        # SQLAdmin は Starlette の Form パースを期待するため data 引数を使用
        response = await client.post("/admin/login", data=login_data)
        assert response.status_code in (302, 303)
        loc = response.headers.get("location")
        assert loc in ("/admin/", "http://test/admin/")

        # セッションCookieを持って /admin/ にアクセス
        dashboard_response = await client.get("/admin/")
        assert dashboard_response.status_code == 200
        assert "admin" in dashboard_response.text.lower()


@pytest.mark.anyio
async def test_admin_portal_login_failure():
    """誤った認証情報でのログインが失敗し、セッションが確立されないことを確認。"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        login_data = {
            "username": "wrong_user",
            "password": "wrong_password",
        }
        response = await client.post("/admin/login", data=login_data)
        # ログイン失敗時はリダイレクトされず、400 Bad Request が返る
        assert response.status_code == 400
