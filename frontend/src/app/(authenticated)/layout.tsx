"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { useUsers } from "@/features/auth/hooks/useUsers";
import { useNotifications } from "@/features/common/notifications/useNotifications";
import { WebSocketProvider } from "@/features/common/websocket/context/WebSocketContext";
import { WorkspaceHeaderContainer } from "@/features/workspace/components/WorkspaceHeaderContainer";
import { WorkspaceLoading } from "@/features/workspace/components/WorkspaceLoading";
import { WorkspaceContext } from "@/features/workspace/context/WorkspaceContext";

export default function AuthenticatedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
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

  function NotificationHandler() {
    useNotifications();
    return null;
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
        <NotificationHandler />
        <div
          style={{ display: "flex", flexDirection: "column", height: "100vh" }}
        >
          <WorkspaceHeaderContainer />
          <div style={{ flex: 1, overflow: "hidden" }}>{children}</div>
        </div>
      </WorkspaceContext.Provider>
    </WebSocketProvider>
  );
}
