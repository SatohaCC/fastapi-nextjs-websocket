export class UnauthorizedError extends Error {
  constructor(url: string) {
    super(`未ログイン (401) at ${url}`);
    this.name = "UnauthorizedError";
  }
}

/**
 * 401 エラー（未ログイン）を検知してグローバルに通知する共通 fetch クライアント。
 */
export async function apiClient(
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<Response> {
  const headers = new Headers(init?.headers);
  headers.set("X-Requested-With", "XMLHttpRequest");

  const res = await fetch(input, {
    ...init,
    headers,
  });

  if (res.status === 401) {
    if (typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent("unauthorized"));
    }
    const url = typeof input === "string" ? input : (input as URL).toString();
    throw new UnauthorizedError(url);
  }

  return res;
}
