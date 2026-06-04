import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { API_BASE } from "@/lib/config";
import {
  applyRefreshedCookies,
  attemptTokenRefresh,
  decryptSession,
  REFRESH_COOKIE,
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

    if (!sessionCookie) {
      return NextResponse.json({ detail: "未ログイン" }, { status: 401 });
    }

    const token = await decryptSession(sessionCookie.value);
    if (!token) {
      return NextResponse.json(
        { detail: "セッションが無効です" },
        { status: 401 },
      );
    }

    const res = await fetchTicket(token);

    if (res.status === 401) {
      const refreshed = await attemptTokenRefresh(
        cookieStore.get(REFRESH_COOKIE)?.value,
      );
      if (!refreshed) {
        return NextResponse.json(
          { detail: "再ログインが必要です" },
          { status: 401 },
        );
      }

      const retryRes = await fetchTicket(refreshed.accessToken);
      if (!retryRes.ok) {
        if (retryRes.status === 401) {
          return NextResponse.json(
            { detail: "再ログインが必要です" },
            { status: 401 },
          );
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
    return NextResponse.json(data);
  } catch (error) {
    // biome-ignore lint/suspicious/noConsole: Error tracking
    console.error("[BFF WsTicket] Error:", error);
    return NextResponse.json(
      { detail: "Internal Server Error" },
      { status: 500 },
    );
  }
}
