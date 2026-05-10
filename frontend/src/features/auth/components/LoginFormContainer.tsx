"use client";

import { useLoginForm } from "@/features/auth/hooks/useLoginForm";
import { LoginForm } from "./LoginForm";

export function LoginFormContainer() {
  const {
    username,
    setUsername,
    password,
    setPassword,
    error,
    loading,
    handleSubmit,
  } = useLoginForm();

  return (
    <LoginForm
      username={username}
      password={password}
      error={error}
      loading={loading}
      onUsernameChange={setUsername}
      onPasswordChange={setPassword}
      onSubmit={handleSubmit}
    />
  );
}
