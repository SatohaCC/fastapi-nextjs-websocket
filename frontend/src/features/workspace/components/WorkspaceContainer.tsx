"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { useUsers } from "@/features/auth/hooks/useUsers";
import { WebSocketProvider } from "@/features/common/websocket/context/WebSocketContext";
import { WorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import { Workspace } from "./Workspace";
import { WorkspaceLoading } from "./WorkspaceLoading";

export function WorkspaceContainer() {
  const router = useRouter();
  const { token, username, isSessionLoaded, clearSession } = useAuth();
  const { users, loading: usersLoading } = useUsers(token);

  useEffect(() => {
    if (isSessionLoaded && (!token || !username)) {
      router.replace("/");
    }
  }, [isSessionLoaded, token, username, router]);

  const handleLogout = () => {
    clearSession();
    router.replace("/");
  };

  if (!isSessionLoaded || usersLoading || !username) {
    return <WorkspaceLoading />;
  }

  return (
    <WebSocketProvider token={token}>
      <WorkspaceContext.Provider
        value={{ username, users, onLogout: handleLogout }}
      >
        <Workspace token={token} />
      </WorkspaceContext.Provider>
    </WebSocketProvider>
  );
}
