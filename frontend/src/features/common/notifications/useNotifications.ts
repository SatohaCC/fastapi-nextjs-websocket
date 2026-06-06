"use client";

import { useCallback } from "react";
import { useWsSubscribe } from "@/features/common/websocket/hooks/useWsSubscribe";
import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import { showBrowserNotification } from "@/lib/browserNotification";
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
      const title = "グローバルチャット";
      const description = `${data.username}: ${data.text}`;
      toast.message(title, { description });
      if (settings.browserNotification) {
        showBrowserNotification(title, description);
      }
    },
    [username, settings.globalChat, settings.browserNotification],
  );

  const handleDirectRequest = useCallback(
    (data: DirectRequestServerMessage) => {
      if (!settings.directRequest) return;
      if (data.is_history || data.recipient !== username) return;
      const title = `${data.sender} からリクエスト`;
      toast.message(title, { description: data.text });
      if (settings.browserNotification) {
        showBrowserNotification(title, data.text);
      }
    },
    [username, settings.directRequest, settings.browserNotification],
  );

  const handleDirectRequestUpdated = useCallback(
    (data: DirectRequestUpdatedServerMessage) => {
      if (!settings.directRequestUpdated) return;
      if (data.is_history || data.sender !== username) return;
      const label =
        data.status === "processing" ? "承諾されました" : "完了しました";
      const title = `リクエストが${label}`;
      const description = `${data.recipient} が対応`;
      toast.message(title, { description });
      if (settings.browserNotification) {
        showBrowserNotification(title, description);
      }
    },
    [username, settings.directRequestUpdated, settings.browserNotification],
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
