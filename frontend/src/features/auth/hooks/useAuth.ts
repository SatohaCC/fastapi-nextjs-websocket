"use client";

import { useCallback, useEffect, useState } from "react";

export interface UseAuthResult {
  token: string | null;
  username: string | null;
  isSessionLoaded: boolean;
  setSession: (token: string, username: string) => void;
  clearSession: () => void;
}

export function useAuth(): UseAuthResult {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);
  const [isSessionLoaded, setIsSessionLoaded] = useState(false);

  useEffect(() => {
    const t = sessionStorage.getItem("token");
    const u = sessionStorage.getItem("username");
    if (t && u) {
      setToken(t);
      setUsername(u);
    }
    setIsSessionLoaded(true);
  }, []);

  const setSession = useCallback((newToken: string, newUsername: string) => {
    sessionStorage.setItem("token", newToken);
    sessionStorage.setItem("username", newUsername);
    setToken(newToken);
    setUsername(newUsername);
  }, []);

  const clearSession = useCallback(() => {
    sessionStorage.removeItem("token");
    sessionStorage.removeItem("username");
    setToken(null);
    setUsername(null);
  }, []);

  return { token, username, isSessionLoaded, setSession, clearSession };
}
