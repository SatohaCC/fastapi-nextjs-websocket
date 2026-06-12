import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { API_BASE } from "@/lib/config";
import {
  clearSessionCookies,
  decryptSession,
  REFRESH_COOKIE,
} from "@/lib/server/session";

export async function POST() {
  const cookieStore = await cookies();
  const refreshCookie = cookieStore.get(REFRESH_COOKIE);

  if (refreshCookie) {
    const refreshToken = await decryptSession(refreshCookie.value);
    if (refreshToken) {
      try {
        await fetch(`${API_BASE}/api/auth/logout`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
      } catch (error) {
        // バックエンドへの呼び出しが失敗しても、フロントエンドのログアウト処理（Cookie削除）は継続する
        // biome-ignore lint/suspicious/noConsole: Error tracking
        console.error("[BFF Logout] Backend logout failed:", error);
      }
    }
  }

  const response = NextResponse.json({ success: true });
  clearSessionCookies(response);
  return response;
}
