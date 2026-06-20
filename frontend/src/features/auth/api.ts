import { apiClient } from "@/lib/apiClient";

export async function login(
  userid: string,
  password: string,
): Promise<{ id: string; userid: string; username: string }> {
  const res = await fetch("/api/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Requested-With": "XMLHttpRequest",
    },
    body: JSON.stringify({ userid, password }),
  });

  if (!res.ok) {
    const err = await res
      .json()
      .catch(() => ({ detail: "ログインに失敗しました" }));
    throw new Error(err.detail || "ログインに失敗しました");
  }

  return res.json();
}

export async function logout(): Promise<void> {
  await fetch("/api/auth/logout", {
    method: "POST",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
  });
}

export async function getMe(): Promise<{
  id: string;
  userid: string;
  username: string;
} | null> {
  try {
    const res = await fetch("/api/auth/me");
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export interface UserListItem {
  id: string;
  username: string;
}

export async function fetchUsers(): Promise<UserListItem[]> {
  const res = await apiClient("/api/proxy/auth/users");

  if (!res.ok) {
    const errorBody = await res.text().catch(() => "unknown");
    throw new Error(
      `ユーザーリストの取得に失敗しました (Status: ${res.status}, Body: ${errorBody})`,
    );
  }

  return res.json();
}

export interface ActiveSession {
  id: string;
  created_at: string;
  ip_address: string;
  user_agent: string;
  is_current: boolean;
}

export async function fetchActiveSessions(): Promise<ActiveSession[]> {
  const res = await apiClient("/api/auth/sessions");
  if (!res.ok) {
    const errorBody = await res.text().catch(() => "unknown");
    throw new Error(
      `セッション一覧の取得に失敗しました (Status: ${res.status}, Body: ${errorBody})`,
    );
  }
  return res.json();
}

export async function revokeSession(sessionId: string): Promise<void> {
  const res = await apiClient(`/api/auth/sessions?id=${sessionId}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const errorBody = await res.text().catch(() => "unknown");
    throw new Error(
      `セッションの切断に失敗しました (Status: ${res.status}, Body: ${errorBody})`,
    );
  }
}

export async function registerUser(
  userid: string,
  username: string,
  password: string,
): Promise<void> {
  const res = await fetch("/api/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Requested-With": "XMLHttpRequest",
    },
    body: JSON.stringify({ userid, username, password }),
  });

  if (!res.ok) {
    const err = await res
      .json()
      .catch(() => ({ detail: "新規登録に失敗しました" }));
    throw new Error(err.detail || "新規登録に失敗しました");
  }
}

export async function unregisterUser(): Promise<void> {
  const res = await fetch("/api/auth/unregister", {
    method: "DELETE",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
  });

  if (!res.ok) {
    const err = await res
      .json()
      .catch(() => ({ detail: "退会処理に失敗しました" }));
    throw new Error(err.detail || "退会処理に失敗しました");
  }
}

export async function changePassword(
  currentPassword: string,
  newPassword: string,
): Promise<void> {
  const res = await apiClient("/api/proxy/auth/change-password", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
    }),
  });

  if (!res.ok) {
    const err = await res
      .json()
      .catch(() => ({ detail: "パスワードの変更に失敗しました" }));
    throw new Error(err.detail || "パスワードの変更に失敗しました");
  }
}

export async function forgotPassword(userid: string): Promise<void> {
  const res = await fetch("/api/auth/forgot-password", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Requested-With": "XMLHttpRequest",
    },
    body: JSON.stringify({ userid }),
  });

  if (!res.ok) {
    const err = await res
      .json()
      .catch(() => ({ detail: "パスワードリセット要求に失敗しました" }));
    throw new Error(err.detail || "パスワードリセット要求に失敗しました");
  }
}

export async function resetPassword(
  token: string,
  newPassword: string,
): Promise<void> {
  const res = await fetch("/api/auth/reset-password", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Requested-With": "XMLHttpRequest",
    },
    body: JSON.stringify({ token, new_password: newPassword }),
  });

  if (!res.ok) {
    const err = await res
      .json()
      .catch(() => ({ detail: "パスワード再設定に失敗しました" }));
    throw new Error(err.detail || "パスワード再設定に失敗しました");
  }
}

export async function updateUsername(
  newUsername: string,
): Promise<{ userid: string; username: string }> {
  const res = await apiClient("/api/proxy/auth/me", {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username: newUsername }),
  });

  if (!res.ok) {
    const err = await res
      .json()
      .catch(() => ({ detail: "ユーザー名の変更に失敗しました" }));
    throw new Error(err.detail || "ユーザー名の変更に失敗しました");
  }
  return res.json();
}
