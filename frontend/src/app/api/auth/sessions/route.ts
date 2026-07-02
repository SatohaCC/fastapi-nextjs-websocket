import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { API_BASE } from "@/lib/config";
import {
  applyRefreshedCookies,
  attemptTokenRefresh,
  clearSessionCookies,
  decryptSession,
  REFRESH_COOKIE,
  SESSION_COOKIE,
} from "@/lib/server/session";

// ヘッダー作成用の共通関数
const buildHeaders = (accessToken: string): Headers => {
  const h = new Headers();
  h.set("Authorization", `Bearer ${accessToken}`);
  return h;
};

// トークン解決用の共通関数 (API Proxyと同様)
async function resolveToken(cookieStore: any) {
  const sessionCookie = cookieStore.get(SESSION_COOKIE);
  let preRefreshResult = null;
  let token = null;

  if (!sessionCookie) {
    preRefreshResult = await attemptTokenRefresh(
      cookieStore.get(REFRESH_COOKIE)?.value,
    );
    if (!preRefreshResult) return null;
    token = preRefreshResult.accessToken;
  } else {
    token = await decryptSession(sessionCookie.value);
    if (!token) return null;
  }
  return { token, preRefreshResult };
}

export async function GET() {
  try {
    const cookieStore = await cookies();
    const refreshCookie = cookieStore.get(REFRESH_COOKIE);
    if (!refreshCookie) {
      const response = NextResponse.json(
        { detail: "未ログイン" },
        { status: 401 },
      );
      clearSessionCookies(response);
      return response;
    }

    // トークンの解決
    const tokenInfo = await resolveToken(cookieStore);
    if (!tokenInfo) {
      const response = NextResponse.json(
        { detail: "未ログイン" },
        { status: 401 },
      );
      clearSessionCookies(response);
      return response;
    }
    const { token, preRefreshResult } = tokenInfo;

    const res = await fetch(`${API_BASE}/api/auth/sessions`, {
      method: "GET",
      headers: buildHeaders(token),
    });

    if (res.status === 401) {
      // リフレッシュを試みる
      const refreshed = await attemptTokenRefresh(refreshCookie.value);
      if (!refreshed) {
        const response = NextResponse.json(
          { detail: "再ログインが必要です" },
          { status: 401 },
        );
        clearSessionCookies(response);
        return response;
      }

      const retryRes = await fetch(`${API_BASE}/api/auth/sessions`, {
        method: "GET",
        headers: buildHeaders(refreshed.accessToken),
      });

      if (!retryRes.ok) {
        const errorData = await retryRes.json().catch(() => ({}));
        return NextResponse.json(
          { detail: errorData.detail || "セッション取得失敗" },
          { status: retryRes.status },
        );
      }

      const sessions = await retryRes.json();
      const response = NextResponse.json(sessions);
      applyRefreshedCookies(response, refreshed);
      return response;
    }

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      return NextResponse.json(
        { detail: errorData.detail || "セッション取得失敗" },
        { status: res.status },
      );
    }

    const sessions = await res.json();
    const response = NextResponse.json(sessions);
    if (preRefreshResult) {
      applyRefreshedCookies(response, preRefreshResult);
    }
    return response;
  } catch (error) {
    console.error("[BFF Sessions GET] Error:", error);
    return NextResponse.json(
      { detail: "Internal Server Error" },
      { status: 500 },
    );
  }
}

export async function DELETE(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get("id");
    if (!sessionId) {
      return NextResponse.json(
        { detail: "セッションIDが必要です" },
        { status: 400 },
      );
    }

    const cookieStore = await cookies();
    const refreshCookie = cookieStore.get(REFRESH_COOKIE);
    if (!refreshCookie) {
      const response = NextResponse.json(
        { detail: "未ログイン" },
        { status: 401 },
      );
      clearSessionCookies(response);
      return response;
    }

    // トークン解決
    const tokenInfo = await resolveToken(cookieStore);
    if (!tokenInfo) {
      const response = NextResponse.json(
        { detail: "未ログイン" },
        { status: 401 },
      );
      clearSessionCookies(response);
      return response;
    }
    const { token, preRefreshResult } = tokenInfo;

    // 自セッション判定のために、セッション一覧を取得
    const sessionsRes = await fetch(`${API_BASE}/api/auth/sessions`, {
      method: "GET",
      headers: buildHeaders(token),
    });

    let isCurrentRevoked = false;
    if (sessionsRes.ok) {
      const sessions = await sessionsRes.json();
      const targetSession = sessions.find((s: any) => s.id === sessionId);
      if (targetSession?.is_current) {
        isCurrentRevoked = true;
      }
    }

    const res = await fetch(`${API_BASE}/api/auth/sessions/${sessionId}`, {
      method: "DELETE",
      headers: buildHeaders(token),
    });

    if (res.status === 401) {
      const refreshed = await attemptTokenRefresh(refreshCookie.value);
      if (!refreshed) {
        const response = NextResponse.json(
          { detail: "再ログインが必要です" },
          { status: 401 },
        );
        clearSessionCookies(response);
        return response;
      }

      const retryRes = await fetch(
        `${API_BASE}/api/auth/sessions/${sessionId}`,
        {
          method: "DELETE",
          headers: buildHeaders(refreshed.accessToken),
        },
      );

      if (!retryRes.ok) {
        const errorData = await retryRes.json().catch(() => ({}));
        return NextResponse.json(
          { detail: errorData.detail || "セッション削除失敗" },
          { status: retryRes.status },
        );
      }

      const response = NextResponse.json({ success: true });
      if (isCurrentRevoked) {
        clearSessionCookies(response);
      } else {
        applyRefreshedCookies(response, refreshed);
      }
      return response;
    }

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      return NextResponse.json(
        { detail: errorData.detail || "セッション削除失敗" },
        { status: res.status },
      );
    }

    const response = NextResponse.json({ success: true });
    if (isCurrentRevoked) {
      clearSessionCookies(response);
    } else if (preRefreshResult) {
      applyRefreshedCookies(response, preRefreshResult);
    }
    return response;
  } catch (error) {
    console.error("[BFF Sessions DELETE] Error:", error);
    return NextResponse.json(
      { detail: "Internal Server Error" },
      { status: 500 },
    );
  }
}
