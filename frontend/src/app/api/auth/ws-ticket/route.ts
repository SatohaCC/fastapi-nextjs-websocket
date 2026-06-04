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

    const res = await fetch(`${API_BASE}/api/auth/ws-ticket`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });

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
