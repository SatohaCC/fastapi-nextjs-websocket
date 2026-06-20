"use client";

import { useCallback, useEffect, useState } from "react";
import { type ActiveSession, fetchActiveSessions, revokeSession } from "../api";

export function useSessions() {
  const [sessions, setSessions] = useState<ActiveSession[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadSessions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchActiveSessions();
      // is_current を先頭にし、その他は作成日時の降順にソートする
      const sorted = [...data].sort((a, b) => {
        if (a.is_current && !b.is_current) return -1;
        if (!a.is_current && b.is_current) return 1;
        return (
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
      });
      setSessions(sorted);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "セッションの取得に失敗しました",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  const handleRevokeSession = useCallback(async (sessionId: string) => {
    try {
      await revokeSession(sessionId);
      // ローカル状態を更新
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
    } catch (err) {
      alert(
        err instanceof Error ? err.message : "セッションの切断に失敗しました",
      );
    }
  }, []);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  return {
    sessions,
    loading,
    error,
    refreshSessions: loadSessions,
    revokeSession: handleRevokeSession,
  };
}
