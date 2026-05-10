"use client";

import { useRouter } from "next/navigation";
import { useActionState, useState } from "react";
import { login } from "@/features/auth/api";

export type LoginFormState = {
  error: string | null;
};

export function useLoginForm() {
  const [username, setUsername] = useState("alice");
  const [password, setPassword] = useState("password1");
  const router = useRouter();

  const [state, formAction, isPending] = useActionState(
    async (
      _prevState: LoginFormState,
      _formData: FormData,
    ): Promise<LoginFormState> => {
      try {
        // Controlled components の状態を使用（または formData から取得も可能）
        const token = await login(username, password);
        sessionStorage.setItem("token", token);
        sessionStorage.setItem("username", username);
        router.push("/workspace");
        return { error: null };
      } catch (err: unknown) {
        return {
          error:
            err instanceof Error ? err.message : "An unknown error occurred",
        };
      }
    },
    { error: null },
  );

  return {
    username,
    setUsername,
    password,
    setPassword,
    error: state.error,
    loading: isPending,
    formAction,
  };
}
