"use client";

import { DirectRequestPanelContainer } from "@/features/direct_request/components/DirectRequestPanelContainer";
import { GlobalChatContainer } from "@/features/global_chat/components/GlobalChatContainer";
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
        <DirectRequestPanelContainer />
      </main>

      <footer className={styles.footer}>
        <p className={styles.footerText}>
          &copy; 2026 Satoha. All rights reserved.
        </p>
      </footer>
    </div>
  );
}
