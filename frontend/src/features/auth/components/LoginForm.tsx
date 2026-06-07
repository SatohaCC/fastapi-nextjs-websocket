"use client";

import { Button } from "@/components/ui/Button/Button";
import { Input } from "@/components/ui/Input/Input";
import { css } from "@/styled-system/css";

const ACCOUNTS = [
  { username: "alice", password: "password1" },
  { username: "bob", password: "password2" },
  { username: "charlie", password: "password3" },
];

const containerStyles = css({
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  height: "100vh",
  background: "black",
  overflow: "hidden",
});

const formStyles = css({
  padding: "32px",
  width: "100%",
  maxWidth: "360px",
  display: "flex",
  flexDirection: "column",
  gap: "16px",
});

const headerStyles = css({
  textAlign: "center",
  marginBottom: "4px",
});

const logoStyles = css({
  fontSize: "22px",
  fontWeight: 900,
  color: "white",
});

const subtitleStyles = css({
  fontSize: "14px",
  color: "textSecondary",
  marginTop: "8px",
});

const accountsStyles = css({
  border: "1px solid",
  borderColor: "panelBorder",
  borderRadius: "8px",
  overflow: "hidden",
});

const accountsLabelStyles = css({
  fontSize: "11px",
  color: "textSecondary",
  padding: "7px 12px",
  borderBottom: "1px solid",
  borderColor: "panelBorder",
});

const accountItemStyles = css({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  padding: "8px 12px",
  width: "100%",
  background: "transparent",
  border: "none",
  borderBottom: "1px solid",
  borderColor: "panelBorder",
  color: "white",
  cursor: "pointer",
  fontSize: "13px",
  transition: "background 0.15s",
  textAlign: "left",
  _last: {
    borderBottom: "none",
  },
  _hover: {
    background: "rgba(255, 255, 255, 0.05)",
  },
});

const accountItemActiveStyles = css({
  background: "rgba(29, 155, 240, 0.12)!",
  borderLeft: "2px solid",
  borderLeftColor: "primary",
  paddingLeft: "10px",
});

const accountNameStyles = css({
  fontWeight: 700,
});

const accountPasswordStyles = css({
  fontSize: "12px",
  color: "textSecondary",
  fontFamily: "monospace",
});

const errorBoxStyles = css({
  padding: "12px",
  background: "rgba(244, 33, 46, 0.1)",
  color: "error",
  borderRadius: "4px",
  fontSize: "13px",
  textAlign: "center",
  border: "1px solid rgba(244, 33, 46, 0.2)",
});

const fieldGroupStyles = css({
  display: "flex",
  flexDirection: "column",
  gap: "4px",
});

const inputStyles = css({
  padding: "12px 16px",
  fontSize: "14px",
});

const submitButtonStyles = css({
  padding: "12px",
  fontSize: "15px",
  width: "100%",
});

export interface LoginFormProps {
  username: string;
  password: string;
  error: string | null;
  loading: boolean;
  onUsernameChange: (value: string) => void;
  onPasswordChange: (value: string) => void;
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
}

export function LoginForm({
  username,
  password,
  error,
  loading,
  onUsernameChange,
  onPasswordChange,
  onSubmit,
}: LoginFormProps) {
  return (
    <div className={containerStyles}>
      <form onSubmit={onSubmit} className={`fade-in ${formStyles}`}>
        <div className={headerStyles}>
          <h1 className={logoStyles}>WebSocket お試しアプリ</h1>
          <p className={subtitleStyles}>
            テスト用アカウントをクリックすると自動入力されます
          </p>
        </div>

        <div className={accountsStyles}>
          <p className={accountsLabelStyles}>テスト用アカウント</p>
          {ACCOUNTS.map((a) => {
            const isActive = username === a.username;
            return (
              <button
                key={a.username}
                type="button"
                className={`${accountItemStyles} ${isActive ? accountItemActiveStyles : ""}`.trim()}
                aria-pressed={isActive}
                onClick={() => {
                  onUsernameChange(a.username);
                  onPasswordChange(a.password);
                }}
              >
                <span
                  className={`${accountNameStyles} ${isActive ? css({ color: "primary" }) : ""}`.trim()}
                >
                  {a.username}
                </span>
                <span className={accountPasswordStyles}>{a.password}</span>
              </button>
            );
          })}
        </div>

        {error && (
          <div className={errorBoxStyles} role="alert" aria-live="assertive">
            {error}
          </div>
        )}

        <div className={fieldGroupStyles}>
          <label htmlFor="username" className="sr-only">
            ユーザー名
          </label>
          <Input
            id="username"
            type="text"
            value={username}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              onUsernameChange(e.target.value)
            }
            required
            placeholder="ユーザー名"
            className={inputStyles}
          />
        </div>

        <div className={fieldGroupStyles}>
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
            className={inputStyles}
          />
        </div>

        <Button
          type="submit"
          disabled={loading}
          variant="primary"
          className={submitButtonStyles}
        >
          {loading ? "ログイン中..." : "ログイン"}
        </Button>
      </form>
    </div>
  );
}
