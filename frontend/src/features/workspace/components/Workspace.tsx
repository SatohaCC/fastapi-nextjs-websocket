"use client";

import { useWebSocketContext } from "@/features/common/websocket/context/WebSocketContext";
import { DirectRequestPanelContainer } from "@/features/direct_request/components/DirectRequestPanelContainer";
import { GlobalChatContainer } from "@/features/global_chat/components/GlobalChatContainer";
import { OnlineUsersContainer } from "@/features/presence/components/OnlineUsersContainer";
import { WorkspaceFooter } from "./WorkspaceFooter/WorkspaceFooter";
import { WorkspaceLayout } from "./WorkspaceLayout/WorkspaceLayout";

export function Workspace() {
  const { error } = useWebSocketContext();

  return (
    <WorkspaceLayout
      presence={<OnlineUsersContainer />}
      footer={<WorkspaceFooter />}
      error={error}
    >
      <GlobalChatContainer />
      <DirectRequestPanelContainer />
    </WorkspaceLayout>
  );
}
