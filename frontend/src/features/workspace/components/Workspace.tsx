"use client";

import { GlobalChatContainer } from "@/features/chat/components/GlobalChatContainer";
import { RequestPanelContainer } from "@/features/requests/components/RequestPanelContainer";
import { WorkspaceHeader } from "@/features/workspace/components/WorkspaceHeader";
import type { ChatMessage, RequestMessage, RequestStatus } from "@/types/ws";
import styles from "./Workspace.module.css";

interface Props {
  username: string | null;
  users: string[];
  chatMessages: ChatMessage[];
  requestMessages: RequestMessage[];
  isConnected: boolean;
  isOnline: boolean;
  error: string | null;
  heartbeatStatus: string;
  syncStatus: string;
  onLogout: () => void;
  onSendChat: (text: string) => void;
  onSendRequest: (to: string, text: string) => void;
  onUpdateStatus: (id: number, status: RequestStatus) => void;
}

export function Workspace({
  username,
  users,
  chatMessages,
  requestMessages,
  isConnected,
  isOnline,
  error,
  heartbeatStatus,
  syncStatus,
  onLogout,
  onSendChat,
  onSendRequest,
  onUpdateStatus,
}: Props) {
  const isActuallyConnected = isConnected && isOnline;

  return (
    <div className={styles.container}>
      <WorkspaceHeader
        username={username}
        isActuallyConnected={isActuallyConnected}
        error={error}
        heartbeatStatus={heartbeatStatus}
        syncStatus={syncStatus}
        onLogout={onLogout}
      />

      {error && (
        <div className={`fade-in ${styles.errorToast}`}>
          System Alert: {error}
        </div>
      )}

      <main className={styles.main}>
        <GlobalChatContainer
          messages={chatMessages}
          onSend={onSendChat}
          currentUser={username || ""}
        />
        <RequestPanelContainer
          users={users}
          messages={requestMessages}
          onSend={onSendRequest}
          onUpdateStatus={onUpdateStatus}
          currentUser={username || ""}
        />
      </main>

      <footer className={styles.footer}>
        <p className={styles.footerText}>
          &copy; 2026 Satoha. All rights reserved.
        </p>
      </footer>
    </div>
  );
}
