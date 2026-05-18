"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { login } from "@/features/auth/api";
import { useAuth } from "@/features/auth/hooks/useAuth";

export function useLoginForm() {
  const [username, setUsername] = useState("alice");
  const [password, setPassword] = useState("password1");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { setSession } = useAuth();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const token = await login(username, password);
      setSession(token, username);
      router.push("/workspace");
    } catch (err: unknown) {
      setError(
        err instanceof Error ? err.message : "An unknown error occurred",
      );
    } finally {
      setLoading(false);
    }
  };

  return {
    username,
    setUsername,
    password,
    setPassword,
    error,
    loading,
    handleSubmit,
  };
}
