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
    const { username, password } = await request.json();

    const res = await fetch(`${API_BASE}/api/auth/token`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
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

    const response = NextResponse.json({ username });
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
