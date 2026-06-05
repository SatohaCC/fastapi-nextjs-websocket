import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { API_BASE } from "@/lib/config";
import {
  applyRefreshedCookies,
  attemptTokenRefresh,
  decryptSession,
  REFRESH_COOKIE,
  type RefreshResult,
  SESSION_COOKIE,
} from "@/lib/server/session";

async function handleProxy(
  request: Request,
  { params }: { params: Promise<{ path: string[] }> },
) {
  try {
    const { path } = await params;
    const destPath = path.join("/");
    const cookieStore = await cookies();
    const sessionCookie = cookieStore.get(SESSION_COOKIE);

    let preRefreshResult: RefreshResult | null = null;
    let token: string | null = null;

    if (!sessionCookie) {
      preRefreshResult = await attemptTokenRefresh(
        cookieStore.get(REFRESH_COOKIE)?.value,
      );
      if (!preRefreshResult) {
        return NextResponse.json({ detail: "未ログイン" }, { status: 401 });
      }
      token = preRefreshResult.accessToken;
    } else {
      token = await decryptSession(sessionCookie.value);
      if (!token) {
        return NextResponse.json(
          { detail: "セッションが無効です" },
          { status: 401 },
        );
      }
    }

    const url = new URL(request.url);
    const destinationUrl = `${API_BASE}/api/${destPath}${url.search}`;

    const buildHeaders = (accessToken: string): Headers => {
      const h = new Headers();
      h.set("Authorization", `Bearer ${accessToken}`);
      const contentType = request.headers.get("content-type");
      if (contentType) h.set("content-type", contentType);
      return h;
    };

    const body = ["GET", "HEAD"].includes(request.method)
      ? undefined
      : await request.arrayBuffer();

    const res = await fetch(destinationUrl, {
      method: request.method,
      // biome-ignore lint/style/noNonNullAssertion: token is guaranteed non-null here (null case returns 401 above)
      headers: buildHeaders(token!),
      body,
    });

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

      const retryRes = await fetch(destinationUrl, {
        method: request.method,
        headers: buildHeaders(refreshed.accessToken),
        body,
      });

      const retryData = await retryRes
        .json()
        .catch(() => ({ detail: "Proxy error" }));
      const response = NextResponse.json(retryData, {
        status: retryRes.status,
      });
      applyRefreshedCookies(response, refreshed);
      return response;
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      return NextResponse.json(err || { detail: "Proxy error" }, {
        status: res.status,
      });
    }

    const data = await res.json().catch(() => null);
    const response = NextResponse.json(data);
    if (preRefreshResult) {
      applyRefreshedCookies(response, preRefreshResult);
    }
    return response;
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
