"use client";

import { useNotifications } from "@/features/common/notifications/useNotifications";
import { useWebSocketContext } from "@/features/common/websocket/context/WebSocketContext";
import { DirectRequestPanelContainer } from "@/features/direct_request/components/DirectRequestPanelContainer";
import { GlobalChatContainer } from "@/features/global_chat/components/GlobalChatContainer";
import { WorkspaceFooter } from "@/features/workspace/components/WorkspaceFooter";
import { WorkspaceHeaderContainer } from "@/features/workspace/components/WorkspaceHeaderContainer";
import {
  containerStyles,
  errorToastStyles,
  mainStyles,
} from "./Workspace.styles";

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
