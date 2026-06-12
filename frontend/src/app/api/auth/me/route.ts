import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { API_BASE } from "@/lib/config";
import {
  applyRefreshedCookies,
  attemptTokenRefresh,
  clearSessionCookies,
  decryptSession,
  REFRESH_COOKIE,
  type RefreshResult,
  SESSION_COOKIE,
} from "@/lib/server/session";

/**
 * 再ログインが必要な 401 レスポンスを生成します。
 *
 * 無効になった Cookie を残すとルートページ（Cookie の有無で判定）と
 * /workspace の間でリダイレクトループになるため、同時に削除します。
 */
const unauthorizedResponse = (detail: string) => {
  const response = NextResponse.json({ detail }, { status: 401 });
  clearSessionCookies(response);
  return response;
};

export async function GET() {
  try {
    const cookieStore = await cookies();
    const sessionCookie = cookieStore.get(SESSION_COOKIE);

    let preRefreshResult: RefreshResult | null = null;
    let token: string | null = null;

    if (!sessionCookie) {
      preRefreshResult = await attemptTokenRefresh(
        cookieStore.get(REFRESH_COOKIE)?.value,
      );
      if (!preRefreshResult) {
        return unauthorizedResponse("未ログイン");
      }
      token = preRefreshResult.accessToken;
    } else {
      token = await decryptSession(sessionCookie.value);
      if (!token) {
        return unauthorizedResponse("セッションが無効です");
      }
    }

    const res = await fetch(`${API_BASE}/api/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (res.status === 401) {
      const refreshed = await attemptTokenRefresh(
        cookieStore.get(REFRESH_COOKIE)?.value,
      );
      if (!refreshed) {
        return unauthorizedResponse("再ログインが必要です");
      }

      const retryRes = await fetch(`${API_BASE}/api/auth/me`, {
        headers: { Authorization: `Bearer ${refreshed.accessToken}` },
      });

      if (!retryRes.ok) {
        if (retryRes.status === 401) {
          return unauthorizedResponse("再ログインが必要です");
        }
        const err = await retryRes.json().catch(() => ({}));
        return NextResponse.json(
          err || { detail: "セッション検証に失敗しました" },
          { status: retryRes.status },
        );
      }

      const data = await retryRes.json();
      const response = NextResponse.json(data);
      applyRefreshedCookies(response, refreshed);
      return response;
    }

    if (!res.ok) {
      return NextResponse.json(
        { detail: "セッション検証に失敗しました" },
        { status: 401 },
      );
    }

    const data = await res.json();
    const response = NextResponse.json(data);
    if (preRefreshResult) {
      applyRefreshedCookies(response, preRefreshResult);
    }
    return response;
  } catch (error) {
    // biome-ignore lint/suspicious/noConsole: Error tracking
    console.error("[BFF Me] Error:", error);
    return NextResponse.json(
      { detail: "Internal Server Error" },
      { status: 500 },
    );
  }
}
