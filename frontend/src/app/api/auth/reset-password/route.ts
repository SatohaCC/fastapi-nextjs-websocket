import { NextResponse } from "next/server";
import { API_BASE } from "@/lib/config";

export async function POST(request: Request) {
  try {
    const body = await request.json();

    const res = await fetch(`${API_BASE}/api/auth/reset-password`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const err = await res
        .json()
        .catch(() => ({ detail: "パスワードリセットに失敗しました" }));
      return NextResponse.json(
        { detail: err.detail || "パスワードリセットに失敗しました" },
        { status: res.status },
      );
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    // biome-ignore lint/suspicious/noConsole: Error tracking
    console.error("[BFF ResetPassword] Error:", error);
    return NextResponse.json(
      { detail: "Internal Server Error" },
      { status: 500 },
    );
  }
}
