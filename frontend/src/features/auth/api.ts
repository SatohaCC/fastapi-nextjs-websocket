import { API_BASE } from "@/lib/config";

export async function login(
  username: string,
  password: string,
): Promise<string> {
  const res = await fetch(`${API_BASE}/api/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "ログインに失敗しました");
  }

  const data = await res.json();
  return data.access_token;
}
