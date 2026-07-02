import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // BFF API ルート (/api/...) に対する CSRF 対策（カスタムヘッダー検証）
  if (pathname.startsWith("/api")) {
    const csrfMethods = ["POST", "PUT", "DELETE", "PATCH"];
    if (csrfMethods.includes(request.method)) {
      const hasCustomHeader = request.headers.has("x-requested-with");
      if (!hasCustomHeader) {
        return new NextResponse(
          JSON.stringify({
            detail: "Forbidden: Custom header validation failed",
          }),
          {
            status: 403,
            headers: { "Content-Type": "application/json" },
          },
        );
      }
    }
    return NextResponse.next();
  }

  const hasRefresh = request.cookies.has("bff_refresh");

  // /workspace 配下のルートガード
  if (pathname.startsWith("/workspace")) {
    if (!hasRefresh) {
      // 未ログインの場合はログイン画面（/）へリダイレクト
      const url = request.nextUrl.clone();
      url.pathname = "/";
      return NextResponse.redirect(url);
    }
  }

  // ログイン画面（/）のガード
  if (pathname === "/") {
    if (hasRefresh) {
      // ログイン済みの場合はワークスペースへリダイレクト
      const url = request.nextUrl.clone();
      url.pathname = "/workspace";
      return NextResponse.redirect(url);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * 以下のパスを除くすべてのリクエストパスにマッチします:
     * - _next/static (静的ファイル)
     * - _next/image (画像最適化ファイル)
     * - favicon.ico, sitemap.xml, robots.txt (メタデータファイル)
     */
    "/((?!_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)",
  ],
};
