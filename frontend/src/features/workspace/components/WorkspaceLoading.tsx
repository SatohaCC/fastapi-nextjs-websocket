"use client";

import styles from "./WorkspaceLoading.module.css";

export interface WorkspaceLoadingProps {
  message?: string;
}

export function WorkspaceLoading({
  message = "Initializing App...",
}: WorkspaceLoadingProps) {
  return (
    <div className={styles.loadingContainer}>
      <div className="fade-in">{message}</div>
    </div>
  );
}
