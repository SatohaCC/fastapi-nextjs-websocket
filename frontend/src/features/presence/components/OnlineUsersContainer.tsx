"use client";

import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import { usePresence } from "../hooks/usePresence";
import { OnlineUsers } from "./OnlineUsers/OnlineUsers";

/**
 * 在席ロスターの Container。usePresence からデータを取得し、
 * Presentational な OnlineUsers に分配する。
 */
export function OnlineUsersContainer() {
  const { onlineUsernames, isReady } = usePresence();
  const { username } = useWorkspaceContext();

  return (
    <OnlineUsers
      usernames={onlineUsernames}
      currentUsername={username}
      isReady={isReady}
    />
  );
}
