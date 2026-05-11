"use client";

import styles from "./WorkspaceLoading.module.css";

interface Props {
  message?: string;
}

export function WorkspaceLoading({ message = "Initializing App..." }: Props) {
  return (
    <div className={styles.loadingContainer}>
      <div className="fade-in">{message}</div>
    </div>
  );
}
