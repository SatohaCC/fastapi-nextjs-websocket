"use client";

import { useWebSocketContext } from "@/features/common/websocket/context/WebSocketContext";
import { DirectRequestPanelContainer } from "@/features/direct_request/components/DirectRequestPanelContainer";
import { GlobalChatContainer } from "@/features/global_chat/components/GlobalChatContainer";
import { WorkspaceHeader } from "@/features/workspace/components/WorkspaceHeader";
import styles from "./Workspace.module.css";

interface WorkspaceProps {
  token: string | null;
}

export function Workspace({ token }: WorkspaceProps) {
  const { error } = useWebSocketContext();

  return (
    <div className={styles.container}>
      <WorkspaceHeader />

      {error && (
        <div className={`fade-in ${styles.errorToast}`}>
          System Alert: {error}
        </div>
      )}

      <main className={styles.main}>
        <GlobalChatContainer token={token} />
        <DirectRequestPanelContainer token={token} />
      </main>

      <footer className={styles.footer}>
        <p className={styles.footerText}>
          &copy; 2026 Satoha. All rights reserved.
        </p>
      </footer>
    </div>
  );
}
