import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { API_BASE } from "@/lib/config";
import { decryptSession } from "@/lib/server/session";

async function handleProxy(
  request: Request,
  { params }: { params: Promise<{ path: string[] }> },
) {
  try {
    const { path } = await params;
    const destPath = path.join("/");
    console.time(`[BFF Proxy] Total: ${destPath}`);
    const cookieStore = await cookies();
    const sessionCookie = cookieStore.get("bff_session");

    if (!sessionCookie) {
      return NextResponse.json({ detail: "未ログイン" }, { status: 401 });
    }

    console.time(`[BFF Proxy] Decrypt: ${destPath}`);
    const token = await decryptSession(sessionCookie.value);
    console.timeEnd(`[BFF Proxy] Decrypt: ${destPath}`);

    if (!token) {
      return NextResponse.json(
        { detail: "セッションが無効です" },
        { status: 401 },
      );
    }

    const url = new URL(request.url);
    const destinationUrl = `${API_BASE}/api/${destPath}${url.search}`;

    const headers = new Headers();
    headers.set("Authorization", `Bearer ${token}`);
    const contentType = request.headers.get("content-type");
    if (contentType) {
      headers.set("content-type", contentType);
    }

    console.time(`[BFF Proxy] Read Body: ${destPath}`);
    const body = ["GET", "HEAD"].includes(request.method)
      ? undefined
      : await request.arrayBuffer(); // Use arrayBuffer instead of blob to see if it is faster
    console.timeEnd(`[BFF Proxy] Read Body: ${destPath}`);

    console.time(`[BFF Proxy] Fetch FastAPI: ${destPath}`);
    const res = await fetch(destinationUrl, {
      method: request.method,
      headers,
      body,
    });
    console.timeEnd(`[BFF Proxy] Fetch FastAPI: ${destPath}`);

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      return NextResponse.json(err || { detail: "Proxy error" }, {
        status: res.status,
      });
    }

    console.time(`[BFF Proxy] Parse JSON: ${destPath}`);
    const data = await res.json().catch(() => null);
    console.timeEnd(`[BFF Proxy] Parse JSON: ${destPath}`);

    console.timeEnd(`[BFF Proxy] Total: ${destPath}`);
    return NextResponse.json(data);
  } catch (error) {
    // biome-ignore lint/suspicious/noConsole: Error tracking
    console.error("[BFF Proxy] Error:", error);
    return NextResponse.json(
      { detail: "Internal Server Error" },
      { status: 500 },
    );
  }
}

export {
  handleProxy as GET,
  handleProxy as POST,
  handleProxy as PUT,
  handleProxy as PATCH,
  handleProxy as DELETE,
};
