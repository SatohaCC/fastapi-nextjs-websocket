"use client";

import { useCallback, useEffect, useState } from "react";
import { getMe, logout } from "../api";

export interface UseAuthResult {
  isAuthenticated: boolean;
  username: string | null;
  isSessionLoaded: boolean;
  setSession: (username: string) => void;
  clearSession: () => void;
}

export function useAuth(): UseAuthResult {
  const [username, setUsername] = useState<string | null>(null);
  const [isSessionLoaded, setIsSessionLoaded] = useState(false);

  useEffect(() => {
    // UIのちらつきを防ぐために、sessionStorageからキャッシュされたユーザー名を読み込みます
    const cachedUser = sessionStorage.getItem("username");
    if (cachedUser) {
      setUsername(cachedUser);
    }

    getMe()
      .then((user) => {
        if (user) {
          setUsername(user.username);
          sessionStorage.setItem("username", user.username);
        } else {
          setUsername(null);
          sessionStorage.removeItem("username");
        }
      })
      .catch(() => {
        setUsername(null);
        sessionStorage.removeItem("username");
      })
      .finally(() => {
        setIsSessionLoaded(true);
      });
  }, []);

  const setSession = useCallback((newUsername: string) => {
    setUsername(newUsername);
    sessionStorage.setItem("username", newUsername);
  }, []);

  const clearSession = useCallback(() => {
    setUsername(null);
    sessionStorage.removeItem("username");
    logout().catch((err) => {
      // biome-ignore lint/suspicious/noConsole: Error tracking
      console.error("[logout] Error:", err);
    });
  }, []);

  return {
    isAuthenticated: !!username,
    username,
    isSessionLoaded,
    setSession,
    clearSession,
  };
}
