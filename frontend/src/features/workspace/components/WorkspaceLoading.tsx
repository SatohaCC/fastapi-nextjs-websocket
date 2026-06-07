"use client";

import { css } from "@/styled-system/css";

const loadingContainerStyles = css({
  height: "100vh",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  background: "black",
  color: "white",
  fontSize: "14px",
  letterSpacing: "0.1em",
});

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
