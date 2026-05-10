"use client";

import { Button } from "@/components/ui/Button/Button";
import { Input } from "@/components/ui/Input/Input";
import styles from "./LoginForm.module.css";

const ACCOUNTS = [
  { username: "alice", password: "password1" },
  { username: "bob", password: "password2" },
  { username: "charlie", password: "password3" },
];

interface Props {
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
}: Props) {
  return (
    <div className={`fade-in ${styles.container}`}>
      <form onSubmit={onSubmit} className={styles.form}>
        <div className={styles.header}>
          <h1 className={styles.logo}>WebSocket お試しアプリ</h1>
          <p className={styles.subtitle}>
            テスト用アカウントをクリックすると自動入力されます
          </p>
        </div>

        <div className={styles.accounts}>
          <p className={styles.accountsLabel}>テスト用アカウント</p>
          {ACCOUNTS.map((a) => (
            <button
              key={a.username}
              type="button"
              className={`${styles.accountItem} ${username === a.username ? styles.accountItemActive : ""}`}
              onClick={() => {
                onUsernameChange(a.username);
                onPasswordChange(a.password);
              }}
            >
              <span className={styles.accountName}>{a.username}</span>
              <span className={styles.accountPassword}>{a.password}</span>
            </button>
          ))}
        </div>

        {error && <div className={styles.errorBox}>{error}</div>}

        <div className={styles.fieldGroup}>
          <Input
            id="username"
            type="text"
            value={username}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              onUsernameChange(e.target.value)
            }
            required
            placeholder="ユーザー名"
            className={styles.input}
            aria-label="ユーザー名"
          />
        </div>

        <div className={styles.fieldGroup}>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(e) => onPasswordChange(e.target.value)}
            required
            placeholder="パスワード"
            className={styles.input}
            aria-label="パスワード"
          />
        </div>

        <Button
          type="submit"
          disabled={loading}
          variant="primary"
          className={styles.submitButton}
        >
          {loading ? "ログイン中..." : "ログイン"}
        </Button>
      </form>
    </div>
  );
}
