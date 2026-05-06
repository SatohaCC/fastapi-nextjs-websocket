import { API_BASE } from "@/lib/config";

export async function fetchUsers(token: string): Promise<string[]> {
  const res = await fetch(`${API_BASE}/api/auth/users`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) {
    const errorBody = await res.text().catch(() => "unknown");
    throw new Error(
      `ユーザーリストの取得に失敗しました (Status: ${res.status}, Body: ${errorBody})`,
    );
  }

  return res.json();
}
