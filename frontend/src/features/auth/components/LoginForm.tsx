"use client";

import { Button } from "@/components/ui/primitives/Button/Button";
import { Input } from "@/components/ui/primitives/Input/Input";
import { css } from "@/styled-system/css";
import { AccountList } from "./AccountList/AccountList";
import {
  AuthError,
  AuthForm,
  AuthHeader,
  AuthLayout,
} from "./AuthLayout/AuthLayout";

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
    <AuthLayout>
      <AuthForm onSubmit={onSubmit}>
        <AuthHeader
          title="WebSocket お試しアプリ"
          subtitle="テスト用アカウントをクリックすると自動入力されます"
        />

        <AccountList
          accounts={ACCOUNTS}
          selectedUsername={username}
          onSelect={(u, p) => {
            onUsernameChange(u);
            onPasswordChange(p);
          }}
        />

        {error && <AuthError message={error} />}

        <div
          className={css({
            display: "flex",
            flexDirection: "column",
            gap: "16px",
          })}
        >
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
          />
        </div>

        <Button
          type="submit"
          disabled={loading}
          variant="primary"
          size="lg"
          fullWidth
        >
          {loading ? "ログイン中..." : "ログイン"}
        </Button>
      </AuthForm>
    </AuthLayout>
  );
}
