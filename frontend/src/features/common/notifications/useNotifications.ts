"use client";

import { useCallback } from "react";
import { useWsSubscribe } from "@/features/common/websocket/hooks/useWsSubscribe";
import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import { toast } from "@/lib/toast";
import type {
  DirectRequestServerMessage,
  DirectRequestUpdatedServerMessage,
  GlobalChatServerMessage,
} from "@/types/ws";
import { useNotificationSettings } from "./useNotificationSettings";

export function useNotifications(): void {
  const { username } = useWorkspaceContext();
  const { settings } = useNotificationSettings();

  const handleGlobalChat = useCallback(
    (data: GlobalChatServerMessage) => {
      if (!settings.globalChat) return;
      if (data.is_history || data.username === username) return;
      toast.message("グローバルチャット", {
        description: `${data.username}: ${data.text}`,
      });
    },
    [username, settings.globalChat],
  );

  const handleDirectRequest = useCallback(
    (data: DirectRequestServerMessage) => {
      if (!settings.directRequest) return;
      if (data.is_history || data.recipient !== username) return;
      toast.message(`${data.sender} からリクエスト`, {
        description: data.text,
      });
    },
    [username, settings.directRequest],
  );

  const handleDirectRequestUpdated = useCallback(
    (data: DirectRequestUpdatedServerMessage) => {
      if (!settings.directRequestUpdated) return;
      if (data.is_history || data.sender !== username) return;
      const label =
        data.status === "processing" ? "承諾されました" : "完了しました";
      toast.message(`リクエストが${label}`, {
        description: `${data.recipient} が対応`,
      });
    },
    [username, settings.directRequestUpdated],
  );

  useWsSubscribe<GlobalChatServerMessage>("global_chat", handleGlobalChat);
  useWsSubscribe<DirectRequestServerMessage>(
    "direct_request",
    handleDirectRequest,
  );
  useWsSubscribe<DirectRequestUpdatedServerMessage>(
    "direct_request_updated",
    handleDirectRequestUpdated,
  );
}
