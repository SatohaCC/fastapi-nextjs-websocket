export async function login(
  username: string,
  password: string,
): Promise<string> {
  const res = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  if (!res.ok) {
    const err = await res
      .json()
      .catch(() => ({ detail: "ログインに失敗しました" }));
    throw new Error(err.detail || "ログインに失敗しました");
  }

  const data = await res.json();
  return data.username;
}

export async function logout(): Promise<void> {
  await fetch("/api/auth/logout", { method: "POST" });
}

export async function getMe(): Promise<{ username: string } | null> {
  try {
    const res = await fetch("/api/auth/me");
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export async function fetchUsers(): Promise<string[]> {
  const res = await fetch("/api/proxy/auth/users");

  if (!res.ok) {
    const errorBody = await res.text().catch(() => "unknown");
    throw new Error(
      `ユーザーリストの取得に失敗しました (Status: ${res.status}, Body: ${errorBody})`,
    );
  }

  return res.json();
}
