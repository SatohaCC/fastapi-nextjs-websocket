"use client";

import { createContext, useContext } from "react";

interface WorkspaceContextValue {
  username: string;
  users: string[];
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
