import { NextResponse } from "next/server";
import { API_BASE } from "@/lib/config";
import {
  encryptSession,
  REFRESH_COOKIE,
  REFRESH_COOKIE_OPTIONS,
  SESSION_COOKIE,
  SESSION_COOKIE_OPTIONS,
} from "@/lib/server/session";

export async function POST(request: Request) {
  try {
    const { userid, password } = await request.json();

    const userAgent = request.headers.get("user-agent");
    const ipAddress =
      request.headers.get("x-forwarded-for") ||
      request.headers.get("x-real-ip");

    const fetchHeaders: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (userAgent) {
      fetchHeaders["User-Agent"] = userAgent;
    }
    if (ipAddress) {
      fetchHeaders["X-Forwarded-For"] = ipAddress;
    }

    const res = await fetch(`${API_BASE}/api/auth/token`, {
      method: "POST",
      headers: fetchHeaders,
      body: JSON.stringify({ userid, password }),
    });

    if (!res.ok) {
      const err = await res
        .json()
        .catch(() => ({ detail: "認証に失敗しました" }));
      return NextResponse.json(
        { detail: err.detail || "ログインに失敗しました" },
        { status: res.status },
      );
    }

    const data = await res.json();
    const [encryptedAccess, encryptedRefresh] = await Promise.all([
      encryptSession(data.access_token),
      encryptSession(data.refresh_token),
    ]);

    // バックエンドからユーザーの最新プロファイルを取得する
    const meRes = await fetch(`${API_BASE}/api/auth/me`, {
      headers: { Authorization: `Bearer ${data.access_token}` },
    });
    let userProfile = { userid, username: userid };
    if (meRes.ok) {
      userProfile = await meRes.json();
    }

    const response = NextResponse.json(userProfile);
    response.cookies.set(
      SESSION_COOKIE,
      encryptedAccess,
      SESSION_COOKIE_OPTIONS,
    );
    response.cookies.set(
      REFRESH_COOKIE,
      encryptedRefresh,
      REFRESH_COOKIE_OPTIONS,
    );

    return response;
  } catch (error) {
    // biome-ignore lint/suspicious/noConsole: Error tracking
    console.error("[BFF Login] Error:", error);
    return NextResponse.json(
      { detail: "Internal Server Error" },
      { status: 500 },
    );
  }
}
