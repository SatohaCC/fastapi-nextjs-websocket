"use client";

import { useEffect, useState } from "react";
import { fetchUsers } from "@/features/workspace/api";

export function useUsers(token: string | null) {
  const [users, setUsers] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }

    setLoading(true);
    fetchUsers(token)
      .then(setUsers)
      .catch((err) => {
        // biome-ignore lint/suspicious/noConsole: API error logging
        console.error("[useUsers] Failed to fetch users:", err);
        setError("Failed to load user list");
      })
      .finally(() => setLoading(false));
  }, [token]);

  return { users, loading, error };
}
