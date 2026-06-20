"use client";

import { useRouter } from "next/navigation";
import { useWebSocketContext } from "@/features/common/websocket/context/WebSocketContext";
import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import { WorkspaceHeader } from "./WorkspaceHeader/WorkspaceHeader";

export function WorkspaceHeaderContainer() {
  const { userid, username, onLogout } = useWorkspaceContext();
  const { isConnected, isOnline, error, heartbeatStatus, syncStatus } =
    useWebSocketContext();
  const router = useRouter();

  return (
    <WorkspaceHeader
      userid={userid}
      username={username}
      onLogout={onLogout}
      isConnected={isConnected}
      isOnline={isOnline}
      error={error}
      heartbeatStatus={heartbeatStatus}
      syncStatus={syncStatus}
      onNavigateToSettings={() => router.push("/settings")}
    />
  );
}
