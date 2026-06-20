"use client";

import { useEffect, useState } from "react";
import { fetchUsers, type UserListItem } from "@/features/auth/api";

export function useUsers(isAuthenticated: boolean) {
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    setLoading(true);
    fetchUsers()
      .then(setUsers)
      .catch((err) => {
        // biome-ignore lint/suspicious/noConsole: API error logging
        console.error("[useUsers] Failed to fetch users:", err);
        setError("Failed to load user list");
      })
      .finally(() => setLoading(false));
  }, [isAuthenticated]);

  return { users, loading, error };
}
