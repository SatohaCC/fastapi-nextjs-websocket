"use client";

import { useNotifications } from "@/features/common/notifications/useNotifications";
import { useWebSocketContext } from "@/features/common/websocket/context/WebSocketContext";
import { DirectRequestPanelContainer } from "@/features/direct_request/components/DirectRequestPanelContainer";
import { GlobalChatContainer } from "@/features/global_chat/components/GlobalChatContainer";
import { WorkspaceFooter } from "@/features/workspace/components/WorkspaceFooter";
import { WorkspaceHeaderContainer } from "@/features/workspace/components/WorkspaceHeaderContainer";
import { css } from "@/styled-system/css";

const containerStyles = css({
  height: "100vh",
  padding: "24px",
  display: "flex",
  flexDirection: "column",
  gap: "24px",
  maxWidth: "1600px",
  margin: "0 auto",
  "@media (max-width: 1024px)": {
    padding: "12px",
    height: "auto",
    minHeight: "100vh",
  },
});

const errorToastStyles = css({
  padding: "12px 20px",
  background: "rgba(239, 68, 68, 0.1)",
  color: "error",
  borderRadius: "12px",
  fontSize: "14px",
  textAlign: "center",
  border: "1px solid rgba(239, 68, 68, 0.2)",
  fontWeight: 500,
});

const mainStyles = css({
  flex: 1,
  display: "grid",
  gridTemplateColumns: "minmax(0, 1fr) minmax(0, 1fr)",
  gridTemplateRows: "auto 1fr auto",
  columnGap: "24px",
  rowGap: 0,
  minHeight: 0,
  "@media (max-width: 1024px)": {
    gridTemplateColumns: "1fr",
    gridTemplateRows: "unset",
    gap: "24px",
    overflowY: "auto",
  },
});

export function Workspace() {
  const { error } = useWebSocketContext();
  useNotifications();

  return (
    <div className={containerStyles}>
      <WorkspaceHeaderContainer />

      {error && (
        <div className={`fade-in ${errorToastStyles}`}>
          System Alert: {error}
        </div>
      )}

      <main className={mainStyles}>
        <GlobalChatContainer />
        <DirectRequestPanelContainer />
      </main>

      <WorkspaceFooter />
    </div>
  );
}
