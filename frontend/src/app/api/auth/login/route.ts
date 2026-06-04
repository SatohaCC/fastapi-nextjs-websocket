import { NextResponse } from "next/server";
import { API_BASE } from "@/lib/config";
import { encryptSession } from "@/lib/server/session";

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
    const encryptedCookie = await encryptSession(data.access_token);

    const response = NextResponse.json({ username });

    response.cookies.set("bff_session", encryptedCookie, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 60 * 24, // 1 day
    });

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
