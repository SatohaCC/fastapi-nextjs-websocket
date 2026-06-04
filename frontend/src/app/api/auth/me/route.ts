import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { API_BASE } from "@/lib/config";
import { decryptSession } from "@/lib/server/session";

export async function GET() {
  try {
    const cookieStore = await cookies();
    const sessionCookie = cookieStore.get("bff_session");

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

    const res = await fetch(`${API_BASE}/api/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!res.ok) {
      return NextResponse.json(
        { detail: "セッション検証に失敗しました" },
        { status: 401 },
      );
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    // biome-ignore lint/suspicious/noConsole: Error tracking
    console.error("[BFF Me] Error:", error);
    return NextResponse.json(
      { detail: "Internal Server Error" },
      { status: 500 },
    );
  }
}
