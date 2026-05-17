"use client";

import { createContext, useContext } from "react";
import type {
  DirectRequestServerMessage,
  GlobalChatServerMessage,
  TaskStatus,
} from "@/types/ws";

interface WorkspaceContextValue {
  username: string;
  users: string[];
  chatMessages: GlobalChatServerMessage[];
  requestMessages: DirectRequestServerMessage[];
  isConnected: boolean;
  isOnline: boolean;
  error: string | null;
  heartbeatStatus: string;
  syncStatus: string;
  onLogout: () => void;
  sendChat: (text: string) => Promise<void>;
  sendRequest: (to: string, text: string) => Promise<void>;
  updateStatus: (taskId: number, status: TaskStatus) => Promise<void>;
}

export const WorkspaceContext = createContext<WorkspaceContextValue | null>(
  null,
);

export function useWorkspaceContext(): WorkspaceContextValue {
  const ctx = useContext(WorkspaceContext);
  if (!ctx)
    throw new Error(
      "useWorkspaceContext must be used within WorkspaceContext.Provider",
    );
  return ctx;
}
