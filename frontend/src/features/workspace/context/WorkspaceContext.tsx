"use client";

import { createContext, useContext } from "react";
import type { ChatMessage, RequestMessage } from "@/types/ws";

interface WorkspaceContextValue {
  username: string;
  authToken: string | null;
  users: string[];
  chatMessages: ChatMessage[];
  requestMessages: RequestMessage[];
  isConnected: boolean;
  isOnline: boolean;
  error: string | null;
  heartbeatStatus: string;
  syncStatus: string;
  onLogout: () => void;
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
