"use client";

import { useLoginForm } from "@/features/auth/hooks/useLoginForm";
import { LoginForm } from "./LoginForm";

export function LoginFormContainer() {
  const {
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
    successMessage,
    loading,
    handleSubmit,
  } = useLoginForm();

  return (
    <LoginForm
      mode={mode}
      onModeChange={setMode}
      userid={userid}
      username={username}
      password={password}
      newPassword={newPassword}
      error={error}
      successMessage={successMessage}
      loading={loading}
      onUseridChange={setUserid}
      onUsernameChange={setUsername}
      onPasswordChange={setPassword}
      onNewPasswordChange={setNewPassword}
      onSubmit={handleSubmit}
    />
  );
}
