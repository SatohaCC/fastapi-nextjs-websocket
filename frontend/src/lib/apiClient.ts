/**
 * 401 エラー（未ログイン）を検知してグローバルに通知する共通 fetch クライアント。
 */
export async function apiClient(
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<Response> {
  const res = await fetch(input, init);

  if (res.status === 401 && typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent("unauthorized"));
  }

  return res;
}
