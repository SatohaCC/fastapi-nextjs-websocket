"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useWebSocket } from "@/features/websocket/hooks/useWebSocket";
import { useUsers } from "@/features/workspace/hooks/useUsers";
import { Workspace } from "./Workspace";
import { WorkspaceLoading } from "./WorkspaceLoading";

export function WorkspaceContainer() {
  const router = useRouter();
  const [username, setUsername] = useState<string | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(null);

  const { users, loading: usersLoading } = useUsers(authToken);

  const {
    chatMessages,
    requestMessages,
    isConnected,
    isOnline,
    error,
    heartbeatStatus,
    syncStatus,
    disconnect,
    sendChat,
    sendRequest,
    updateStatus,
  } = useWebSocket(authToken);

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
    disconnect();
    sessionStorage.removeItem("token");
    sessionStorage.removeItem("username");
    router.replace("/");
  };

  if (usersLoading || !username) {
    return <WorkspaceLoading />;
  }

  return (
    <Workspace
      username={username}
      users={users}
      chatMessages={chatMessages}
      requestMessages={requestMessages}
      isConnected={isConnected}
      isOnline={isOnline}
      error={error}
      heartbeatStatus={heartbeatStatus}
      syncStatus={syncStatus}
      onLogout={handleLogout}
      onSendChat={sendChat}
      onSendRequest={sendRequest}
      onUpdateStatus={updateStatus}
    />
  );
}
