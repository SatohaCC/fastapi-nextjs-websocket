"use client";

import { useNotifications } from "@/features/common/notifications/useNotifications";
import { useWebSocketContext } from "@/features/common/websocket/context/WebSocketContext";
import { DirectRequestPanelContainer } from "@/features/direct_request/components/DirectRequestPanelContainer";
import { GlobalChatContainer } from "@/features/global_chat/components/GlobalChatContainer";
import { WorkspaceFooter } from "@/features/workspace/components/WorkspaceFooter";
import { WorkspaceHeaderContainer } from "@/features/workspace/components/WorkspaceHeaderContainer";
import styles from "./Workspace.module.css";

export function Workspace() {
  const { error } = useWebSocketContext();
  useNotifications();

  return (
    <div className={styles.container}>
      <WorkspaceHeaderContainer />

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
