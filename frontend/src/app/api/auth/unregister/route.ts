import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { API_BASE } from "@/lib/config";
import {
  attemptTokenRefresh,
  clearSessionCookies,
  decryptSession,
  REFRESH_COOKIE,
  SESSION_COOKIE,
} from "@/lib/server/session";

export async function DELETE() {
  try {
    const cookieStore = await cookies();
    const sessionCookie = cookieStore.get(SESSION_COOKIE);

    let token: string | null = null;

    if (!sessionCookie) {
      const preRefreshResult = await attemptTokenRefresh(
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

    const res = await fetch(`${API_BASE}/api/auth/me`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!res.ok) {
      const err = await res
        .json()
        .catch(() => ({ detail: "退会処理に失敗しました" }));
      return NextResponse.json(
        { detail: err.detail || "退会処理に失敗しました" },
        { status: res.status },
      );
    }

    const response = NextResponse.json({ success: true });
    clearSessionCookies(response);
    return response;
  } catch (error) {
    // biome-ignore lint/suspicious/noConsole: Error tracking
    console.error("[BFF Unregister] Error:", error);
    return NextResponse.json(
      { detail: "Internal Server Error" },
      { status: 500 },
    );
  }
}
