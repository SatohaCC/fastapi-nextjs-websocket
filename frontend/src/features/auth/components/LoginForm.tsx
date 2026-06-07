"use client";

import { Button } from "@/components/ui/Button/Button";
import { Input } from "@/components/ui/Input/Input";
import { css } from "@/styled-system/css";
import {
  accountItemActiveStyles,
  accountItemStyles,
  accountNameStyles,
  accountPasswordStyles,
  accountsLabelStyles,
  accountsStyles,
  containerStyles,
  errorBoxStyles,
  fieldGroupStyles,
  formStyles,
  headerStyles,
  inputStyles,
  logoStyles,
  submitButtonStyles,
  subtitleStyles,
} from "./LoginForm.styles";

const ACCOUNTS = [
  { username: "alice", password: "password1" },
  { username: "bob", password: "password2" },
  { username: "charlie", password: "password3" },
];

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
