"use client";

import { createContext, useContext } from "react";

import type { UserListItem } from "@/features/auth/api";

interface WorkspaceContextValue {
  id: string;
  userid: string;
  username: string;
  users: UserListItem[];
  onLogout: () => void;
  updateUsernameState: (newUsername: string) => void;
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
