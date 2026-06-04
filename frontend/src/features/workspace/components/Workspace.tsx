"use client";

import { useWebSocketContext } from "@/features/common/websocket/context/WebSocketContext";
import { DirectRequestPanelContainer } from "@/features/direct_request/components/DirectRequestPanelContainer";
import { GlobalChatContainer } from "@/features/global_chat/components/GlobalChatContainer";
import { WorkspaceFooter } from "@/features/workspace/components/WorkspaceFooter";
import { WorkspaceHeader } from "@/features/workspace/components/WorkspaceHeader";
import styles from "./Workspace.module.css";

export function Workspace() {
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
        <GlobalChatContainer />
        <DirectRequestPanelContainer />
      </main>

      <WorkspaceFooter />
    </div>
  );
}
