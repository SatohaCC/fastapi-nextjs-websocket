"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { useUsers } from "@/features/auth/hooks/useUsers";
import { WebSocketProvider } from "@/features/common/websocket/context/WebSocketContext";
import { DirectRequestProvider } from "@/features/direct_request/context/DirectRequestContext";
import { GlobalChatProvider } from "@/features/global_chat/context/GlobalChatContext";
import { WorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import { Workspace } from "./Workspace";
import { WorkspaceLoading } from "./WorkspaceLoading";

export function WorkspaceContainer() {
  const router = useRouter();
  const {
    isAuthenticated,
    id,
    userid,
    username,
    isSessionLoaded,
    clearSession,
    setSession,
  } = useAuth();
  const {
    users,
    loading: usersLoading,
    error: usersError,
  } = useUsers(isAuthenticated);

  useEffect(() => {
    if (isSessionLoaded && (!isAuthenticated || !userid)) {
      router.replace("/");
    }
  }, [isSessionLoaded, isAuthenticated, userid, router]);

  if (usersError) {
    throw new Error(usersError);
  }

  const handleLogout = async () => {
    await clearSession();
    router.replace("/");
  };

  if (!isSessionLoaded || usersLoading || !id || !userid || !username) {
    return <WorkspaceLoading />;
  }

  return (
    <WebSocketProvider isAuthenticated={isAuthenticated}>
      <WorkspaceContext.Provider
        value={{
          id,
          userid,
          username,
          users,
          onLogout: handleLogout,
          updateUsernameState: (newUsername: string) => {
            setSession(id, userid, newUsername);
          },
        }}
      >
        <GlobalChatProvider isAuthenticated={isAuthenticated}>
          <DirectRequestProvider isAuthenticated={isAuthenticated}>
            <Workspace />
          </DirectRequestProvider>
        </GlobalChatProvider>
      </WorkspaceContext.Provider>
    </WebSocketProvider>
  );
}
