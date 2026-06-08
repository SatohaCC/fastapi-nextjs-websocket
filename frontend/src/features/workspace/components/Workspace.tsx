"use client";

import { WorkspaceLayout } from "@/components/ui/Layout/WorkspaceLayout";
import { WorkspaceFooter } from "@/components/ui/WorkspaceFooter/WorkspaceFooter";
import { useNotifications } from "@/features/common/notifications/useNotifications";
import { useWebSocketContext } from "@/features/common/websocket/context/WebSocketContext";
import { DirectRequestPanelContainer } from "@/features/direct_request/components/DirectRequestPanelContainer";
import { GlobalChatContainer } from "@/features/global_chat/components/GlobalChatContainer";
import { WorkspaceHeaderContainer } from "@/features/workspace/components/WorkspaceHeaderContainer";

export function Workspace() {
  const { error } = useWebSocketContext();
  useNotifications();

  return (
    <WorkspaceLayout
      header={<WorkspaceHeaderContainer />}
      footer={<WorkspaceFooter />}
      error={error}
    >
      <GlobalChatContainer />
      <DirectRequestPanelContainer />
    </WorkspaceLayout>
  );
}
