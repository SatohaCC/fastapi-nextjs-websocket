"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { WebSocketProvider } from "@/features/common/websocket/context/WebSocketContext";
import { WorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import { useUsers } from "@/features/workspace/hooks/useUsers";
import { Workspace } from "./Workspace";
import { WorkspaceLoading } from "./WorkspaceLoading";

export function WorkspaceContainer() {
  const router = useRouter();
  const [username, setUsername] = useState<string | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(null);

  const { users, loading: usersLoading } = useUsers(authToken);

  useEffect(() => {
    const t = sessionStorage.getItem("token");
    const u = sessionStorage.getItem("username");
    if (!t || !u) {
      router.replace("/");
      return;
    }
    setUsername(u);
    setAuthToken(t);
  }, [router]);

  const handleLogout = () => {
    setAuthToken(null);
    sessionStorage.removeItem("token");
    sessionStorage.removeItem("username");
    router.replace("/");
  };

  if (usersLoading || !username) {
    return <WorkspaceLoading />;
  }

  return (
    <WebSocketProvider token={authToken}>
      <WorkspaceContext.Provider
        value={{ username, users, onLogout: handleLogout }}
      >
        <Workspace token={authToken} />
      </WorkspaceContext.Provider>
    </WebSocketProvider>
  );
}
