"use client";

import { GlobalChatContainer } from "@/features/chat/components/GlobalChatContainer";
import { RequestPanelContainer } from "@/features/requests/components/RequestPanelContainer";
import { WorkspaceHeader } from "@/features/workspace/components/WorkspaceHeader";
import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import styles from "./Workspace.module.css";

export function Workspace() {
  const { error } = useWorkspaceContext();

  return (
    <div className={styles.container}>
      <WorkspaceHeader />

      {error && (
        <div className={`fade-in ${styles.errorToast}`}>
          System Alert: {error}
        </div>
      )}

      <main className={styles.main}>
        <GlobalChatContainer />
        <RequestPanelContainer />
      </main>

      <footer className={styles.footer}>
        <p className={styles.footerText}>
          &copy; 2026 Satoha. All rights reserved.
        </p>
      </footer>
    </div>
  );
}
