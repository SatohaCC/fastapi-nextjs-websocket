"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import {
  forgotPassword,
  login,
  registerUser,
  resetPassword,
} from "@/features/auth/api";
import { useAuth } from "@/features/auth/hooks/useAuth";

export type AuthMode =
  | "login"
  | "register"
  | "forgot-password"
  | "reset-password";

export function useLoginForm() {
  const [mode, setMode] = useState<AuthMode>("login");
  const [userid, setUserid] = useState("alice");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("password1");
  const [newPassword, setNewPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const { setSession } = useAuth();

  // If token parameter is present in URL, switch to reset-password mode
  useEffect(() => {
    if (token) {
      setMode("reset-password");
    }
  }, [token]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      if (mode === "login") {
        const {
          id: loggedInId,
          userid: loggedInUserid,
          username: loggedInUsername,
        } = await login(userid, password);
        setSession(loggedInId, loggedInUserid, loggedInUsername);
        router.push("/workspace");
      } else if (mode === "register") {
        await registerUser(userid, username, password);
        setSuccessMessage(
          "アカウント登録が完了しました。ログインしてください。",
        );
        setPassword("");
        setMode("login");
      } else if (mode === "forgot-password") {
        await forgotPassword(userid);
        setSuccessMessage(
          "パスワード再設定用のシミュレーションメールを送信しました（バックエンドのコンソールログを確認してください）。",
        );
      } else if (mode === "reset-password") {
        if (!token) {
          throw new Error(
            "無効なリクエスト：リセットトークンが見つかりません。",
          );
        }
        await resetPassword(token, newPassword);
        setSuccessMessage(
          "パスワードを再設定しました。新しいパスワードでログインしてください。",
        );
        setNewPassword("");
        // Query paramからtokenを除外してログイン画面へ
        router.replace("/");
        setMode("login");
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "エラーが発生しました");
    } finally {
      setLoading(false);
    }
  };

  return {
    mode,
    setMode,
    userid,
    setUserid,
    username,
    setUsername,
    password,
    setPassword,
    newPassword,
    setNewPassword,
    error,
    setError,
    successMessage,
    setSuccessMessage,
    loading,
    handleSubmit,
  };
}
