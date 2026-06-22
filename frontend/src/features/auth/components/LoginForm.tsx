"use client";

import { Button, Input } from "@/components/ui/primitives";
import { css } from "@/styled-system/css";
import type { AuthMode } from "../hooks/useLoginForm";
import { AccountList } from "./AccountList/AccountList";
import {
  AuthError,
  AuthForm,
  AuthHeader,
  AuthLayout,
  AuthSuccess,
} from "./AuthLayout/AuthLayout";
import { fieldsWrapperStyles } from "./LoginForm.styles";

const ACCOUNTS = [
  { username: "alice", password: "password1" },
  { username: "bob", password: "password2" },
  { username: "charlie", password: "password3" },
];

const linkButtonStyles = css({
  background: "none",
  border: "none",
  color: "textSecondary",
  fontSize: "13px",
  cursor: "pointer",
  textDecoration: "underline",
  textAlign: "center",
  "&:hover": {
    color: "textPrimary",
  },
});

const linksRowStyles = css({
  display: "flex",
  justifyContent: "space-between",
  gap: "12px",
  marginTop: "8px",
});

const centerLinkStyles = css({
  display: "flex",
  justifyContent: "center",
  marginTop: "8px",
});

export interface LoginFormProps {
  mode: AuthMode;
  onModeChange: (mode: AuthMode) => void;
  userid: string;
  username: string;
  password: string;
  newPassword?: string;
  error: string | null;
  successMessage?: string | null;
  loading: boolean;
  onUseridChange: (value: string) => void;
  onUsernameChange: (value: string) => void;
  onPasswordChange: (value: string) => void;
  onNewPasswordChange?: (value: string) => void;
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
}

export function LoginForm({
  mode,
  onModeChange,
  userid,
  username,
  password,
  newPassword = "",
  error,
  successMessage,
  loading,
  onUseridChange,
  onUsernameChange,
  onPasswordChange,
  onNewPasswordChange,
  onSubmit,
}: LoginFormProps) {
  const getHeaderInfo = () => {
    switch (mode) {
      case "register":
        return {
          title: "新規アカウント登録",
          subtitle: "新しくアカウントを作成します",
        };
      case "forgot-password":
        return {
          title: "パスワードリセット",
          subtitle: "ユーザーIDを入力してリセットリンク（模擬）を発行します",
        };
      case "reset-password":
        return {
          title: "パスワードの再設定",
          subtitle: "新しいパスワードを入力してください",
        };
      default:
        return {
          title: "WebSocket お試しアプリ",
          subtitle: "テスト用アカウントをクリックすると自動入力されます",
        };
    }
  };

  const headerInfo = getHeaderInfo();

  return (
    <AuthLayout>
      <AuthForm onSubmit={onSubmit}>
        <AuthHeader title={headerInfo.title} subtitle={headerInfo.subtitle} />

        {mode === "login" && (
          <AccountList
            accounts={ACCOUNTS}
            selectedUsername={userid}
            onSelect={(u, p) => {
              onUseridChange(u);
              onPasswordChange(p);
            }}
          />
        )}

        {error && <AuthError message={error} />}
        {successMessage && <AuthSuccess message={successMessage} />}

        <div className={fieldsWrapperStyles}>
          {mode !== "reset-password" && (
            <div>
              <label htmlFor="userid" className="sr-only">
                ユーザーID
              </label>
              <Input
                id="userid"
                type="text"
                value={userid}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  onUseridChange(e.target.value)
                }
                required
                placeholder={
                  mode === "register" ? "ユーザーID (例: alice)" : "ユーザーID"
                }
                disabled={loading}
              />
            </div>
          )}

          {mode === "register" && (
            <div>
              <label htmlFor="username" className="sr-only">
                表示名
              </label>
              <Input
                id="username"
                type="text"
                value={username}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  onUsernameChange(e.target.value)
                }
                required
                placeholder="表示名 (例: かのん)"
                disabled={loading}
              />
            </div>
          )}

          {(mode === "login" || mode === "register") && (
            <div>
              <label htmlFor="password" className="sr-only">
                パスワード
              </label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => onPasswordChange(e.target.value)}
                required
                placeholder="パスワード"
                disabled={loading}
              />
            </div>
          )}

          {mode === "reset-password" && onNewPasswordChange && (
            <div>
              <label htmlFor="newPassword" className="sr-only">
                新しいパスワード
              </label>
              <Input
                id="newPassword"
                type="password"
                value={newPassword}
                onChange={(e) => onNewPasswordChange(e.target.value)}
                required
                placeholder="新しいパスワード"
                disabled={loading}
              />
            </div>
          )}
        </div>

        <Button
          type="submit"
          disabled={loading}
          variant="primary"
          size="lg"
          fullWidth
        >
          {loading
            ? "処理中..."
            : mode === "login"
              ? "ログイン"
              : mode === "register"
                ? "登録する"
                : "送信する"}
        </Button>

        {mode === "login" ? (
          <div className={linksRowStyles}>
            <button
              type="button"
              className={linkButtonStyles}
              onClick={() => {
                onModeChange("register");
                onUseridChange("");
                onUsernameChange("");
                onPasswordChange("");
              }}
            >
              新規登録はこちら
            </button>
            <button
              type="button"
              className={linkButtonStyles}
              onClick={() => {
                onModeChange("forgot-password");
                onUseridChange("");
              }}
            >
              パスワードをお忘れですか？
            </button>
          </div>
        ) : (
          <div className={centerLinkStyles}>
            <button
              type="button"
              className={linkButtonStyles}
              onClick={() => {
                onModeChange("login");
                onUseridChange("alice");
                onUsernameChange("");
                onPasswordChange("password1");
              }}
            >
              ログイン画面に戻る
            </button>
          </div>
        )}
      </AuthForm>
    </AuthLayout>
  );
}
