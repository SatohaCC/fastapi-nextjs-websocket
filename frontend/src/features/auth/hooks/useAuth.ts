"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { resetSettings } from "@/lib/notificationSettings";
import { getMe, logout } from "../api";

export interface UseAuthResult {
  isAuthenticated: boolean;
  id: string | null;
  userid: string | null;
  username: string | null;
  isSessionLoaded: boolean;
  setSession: (id: string, userid: string, username: string) => void;
  clearSession: () => Promise<void>;
}

export function useAuth(): UseAuthResult {
  const [id, setId] = useState<string | null>(null);
  const [userid, setUserid] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);
  const [isSessionLoaded, setIsSessionLoaded] = useState(false);
  const isLoggingOutRef = useRef(false);

  useEffect(() => {
    // UIのちらつきを防ぐために、sessionStorageからキャッシュされたユーザーID・表示名を読み込みます
    const cachedId = sessionStorage.getItem("id");
    const cachedUserid = sessionStorage.getItem("userid");
    const cachedUsername = sessionStorage.getItem("username");
    if (cachedId) {
      setId(cachedId);
    }
    if (cachedUserid) {
      setUserid(cachedUserid);
    }
    if (cachedUsername) {
      setUsername(cachedUsername);
    }

    getMe()
      .then((user) => {
        if (user) {
          setId(user.id);
          setUserid(user.userid);
          setUsername(user.username);
          sessionStorage.setItem("id", user.id);
          sessionStorage.setItem("userid", user.userid);
          sessionStorage.setItem("username", user.username);
        } else {
          setId(null);
          setUserid(null);
          setUsername(null);
          sessionStorage.removeItem("id");
          sessionStorage.removeItem("userid");
          sessionStorage.removeItem("username");
        }
      })
      .catch(() => {
        setId(null);
        setUserid(null);
        setUsername(null);
        sessionStorage.removeItem("id");
        sessionStorage.removeItem("userid");
        sessionStorage.removeItem("username");
      })
      .finally(() => {
        setIsSessionLoaded(true);
      });
  }, []);

  useEffect(() => {
    const handleUnauthorized = async () => {
      if (isLoggingOutRef.current) return;
      isLoggingOutRef.current = true;
      try {
        await logout();
      } catch (err) {
        // biome-ignore lint/suspicious/noConsole: Error tracking
        console.error("[handleUnauthorized] logout failed:", err);
      } finally {
        resetSettings();
        setId(null);
        setUserid(null);
        setUsername(null);
        sessionStorage.removeItem("id");
        sessionStorage.removeItem("userid");
        sessionStorage.removeItem("username");
        isLoggingOutRef.current = false;
      }
    };

    if (typeof window !== "undefined") {
      window.addEventListener("unauthorized", handleUnauthorized);
    }
    return () => {
      if (typeof window !== "undefined") {
        window.removeEventListener("unauthorized", handleUnauthorized);
      }
    };
  }, []);

  const setSession = useCallback(
    (newId: string, newUserid: string, newUsername: string) => {
      setId(newId);
      setUserid(newUserid);
      setUsername(newUsername);
      sessionStorage.setItem("id", newId);
      sessionStorage.setItem("userid", newUserid);
      sessionStorage.setItem("username", newUsername);
    },
    [],
  );

  const clearSession = useCallback(async () => {
    if (isLoggingOutRef.current) return;
    isLoggingOutRef.current = true;
    try {
      await logout();
    } catch (err) {
      // biome-ignore lint/suspicious/noConsole: Error tracking
      console.error("[logout] Error:", err);
    } finally {
      resetSettings();
      setId(null);
      setUserid(null);
      setUsername(null);
      sessionStorage.removeItem("id");
      sessionStorage.removeItem("userid");
      sessionStorage.removeItem("username");
      isLoggingOutRef.current = false;
    }
  }, []);

  return {
    isAuthenticated: !!userid,
    id,
    userid,
    username,
    isSessionLoaded,
    setSession,
    clearSession,
  };
}
