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

async function fetchTicket(accessToken: string): Promise<Response> {
  return fetch(`${API_BASE}/api/auth/ws-ticket`, {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}` },
  });
}

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
        const response = NextResponse.json(
          { detail: "未ログイン" },
          { status: 401 },
        );
        clearSessionCookies(response);
        return response;
      }
      token = preRefreshResult.accessToken;
    } else {
      token = await decryptSession(sessionCookie.value);
      if (!token) {
        const response = NextResponse.json(
          { detail: "セッションが無効です" },
          { status: 401 },
        );
        clearSessionCookies(response);
        return response;
      }
    }

    // biome-ignore lint/style/noNonNullAssertion: token is guaranteed non-null here (null case returns 401 above)
    const res = await fetchTicket(token!);

    if (res.status === 401) {
      const refreshed = await attemptTokenRefresh(
        cookieStore.get(REFRESH_COOKIE)?.value,
      );
      if (!refreshed) {
        const response = NextResponse.json(
          { detail: "再ログインが必要です" },
          { status: 401 },
        );
        clearSessionCookies(response);
        return response;
      }

      const retryRes = await fetchTicket(refreshed.accessToken);
      if (!retryRes.ok) {
        if (retryRes.status === 401) {
          const response = NextResponse.json(
            { detail: "再ログインが必要です" },
            { status: 401 },
          );
          clearSessionCookies(response);
          return response;
        }
        const err = await retryRes.json().catch(() => ({}));
        return NextResponse.json(
          { detail: err.detail || "チケットの発行に失敗しました" },
          { status: retryRes.status },
        );
      }

      const data = await retryRes.json();
      const response = NextResponse.json(data);
      applyRefreshedCookies(response, refreshed);
      return response;
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      return NextResponse.json(
        { detail: err.detail || "チケットの発行に失敗しました" },
        { status: res.status },
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
    console.error("[BFF WsTicket] Error:", error);
    return NextResponse.json(
      { detail: "Internal Server Error" },
      { status: 500 },
    );
  }
}
