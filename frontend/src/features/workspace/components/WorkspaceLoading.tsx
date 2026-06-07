"use client";

import { loadingContainerStyles } from "./WorkspaceLoading.styles";

export interface WorkspaceLoadingProps {
  message?: string;
}

export function WorkspaceLoading({
  message = "Initializing App...",
}: WorkspaceLoadingProps) {
  return (
    <div className={loadingContainerStyles}>
      <div className="fade-in">{message}</div>
    </div>
  );
}
