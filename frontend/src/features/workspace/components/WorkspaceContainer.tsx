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
  const { isAuthenticated, username, isSessionLoaded, clearSession } =
    useAuth();
  const {
    users,
    loading: usersLoading,
    error: usersError,
  } = useUsers(isAuthenticated);

  useEffect(() => {
    if (isSessionLoaded && (!isAuthenticated || !username)) {
      router.replace("/");
    }
  }, [isSessionLoaded, isAuthenticated, username, router]);

  if (usersError) {
    throw new Error(usersError);
  }

  const handleLogout = () => {
    clearSession();
    router.replace("/");
  };

  if (!isSessionLoaded || usersLoading || !username) {
    return <WorkspaceLoading />;
  }

  return (
    <WebSocketProvider isAuthenticated={isAuthenticated}>
      <WorkspaceContext.Provider
        value={{ username, users, onLogout: handleLogout }}
      >
        <Workspace />
      </WorkspaceContext.Provider>
    </WebSocketProvider>
  );
}
