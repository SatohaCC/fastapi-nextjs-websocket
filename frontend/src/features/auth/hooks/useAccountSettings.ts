"use client";

import { useEffect, useState } from "react";
import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import { changePassword, unregisterUser, updateUsername } from "../api";

export function useAccountSettings() {
  const { username, updateUsernameState, onLogout } = useWorkspaceContext();

  const [newUsername, setNewUsername] = useState(username || "");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");

  // Sync newUsername when username changes
  useEffect(() => {
    if (username) {
      setNewUsername(username);
    }
  }, [username]);

  const [profileError, setProfileError] = useState<string | null>(null);
  const [profileSuccess, setProfileSuccess] = useState<string | null>(null);
  const [profileLoading, setProfileLoading] = useState(false);

  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [passwordSuccess, setPasswordSuccess] = useState<string | null>(null);
  const [passwordLoading, setPasswordLoading] = useState(false);

  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const handleUpdateUsername = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileLoading(true);
    setProfileError(null);
    setProfileSuccess(null);

    try {
      if (!newUsername.trim()) {
        throw new Error("表示名を入力してください");
      }
      const data = await updateUsername(newUsername);
      updateUsernameState(data.username);
      setProfileSuccess("表示名を変更しました。");
      return true;
    } catch (err: unknown) {
      setProfileError(
        err instanceof Error ? err.message : "表示名の変更に失敗しました",
      );
      return false;
    } finally {
      setProfileLoading(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordLoading(true);
    setPasswordError(null);
    setPasswordSuccess(null);

    try {
      if (!currentPassword || !newPassword) {
        throw new Error("すべてのフィールドを入力してください");
      }
      await changePassword(currentPassword, newPassword);
      setPasswordSuccess(
        "パスワードを変更しました。他のセッションは切断されました。",
      );
      setCurrentPassword("");
      setNewPassword("");
      return true;
    } catch (err: unknown) {
      setPasswordError(
        err instanceof Error ? err.message : "パスワードの変更に失敗しました",
      );
      return false;
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    const confirmed = window.confirm(
      "本当に退会しますか？送信したメッセージやダイレクトリクエスト履歴を含むすべてのアカウントデータが物理削除され、即座にログアウトします。この操作は取り消せません。",
    );
    if (!confirmed) return;

    setDeleteLoading(true);
    setDeleteError(null);

    try {
      await unregisterUser();
      await onLogout();
      window.location.href = "/";
    } catch (err: unknown) {
      setDeleteError(
        err instanceof Error ? err.message : "退会処理に失敗しました",
      );
      setDeleteLoading(false);
    }
  };

  return {
    newUsername,
    setNewUsername,
    currentPassword,
    setCurrentPassword,
    newPassword,
    setNewPassword,
    profileError,
    profileSuccess,
    profileLoading,
    passwordError,
    passwordSuccess,
    passwordLoading,
    deleteError,
    deleteLoading,
    handleUpdateUsername,
    handleChangePassword,
    handleDeleteAccount,
  };
}
