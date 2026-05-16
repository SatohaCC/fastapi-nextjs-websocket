"use client";

import { createContext, useContext } from "react";
import type {
  GlobalChatMessage,
  RequestMessage,
  RequestStatus,
} from "@/types/ws";

interface WorkspaceContextValue {
  username: string;
  users: string[];
  chatMessages: GlobalChatMessage[];
  requestMessages: RequestMessage[];
  isConnected: boolean;
  isOnline: boolean;
  error: string | null;
  heartbeatStatus: string;
  syncStatus: string;
  onLogout: () => void;
  sendChat: (text: string) => Promise<void>;
  sendRequest: (to: string, text: string) => Promise<void>;
  updateStatus: (requestId: number, status: RequestStatus) => Promise<void>;
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
