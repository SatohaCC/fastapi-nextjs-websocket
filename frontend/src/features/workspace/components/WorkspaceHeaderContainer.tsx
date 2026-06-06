"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useNotificationSettings } from "@/features/common/notifications/useNotificationSettings";
import { useWebSocketContext } from "@/features/common/websocket/context/WebSocketContext";
import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import { requestBrowserNotificationPermission } from "@/lib/browserNotification";
import type { NotificationSettings } from "@/lib/notificationSettings";
import { toast } from "@/lib/toast";
import { WorkspaceHeader } from "./WorkspaceHeader";

export function WorkspaceHeaderContainer() {
  const { username, onLogout } = useWorkspaceContext();
  const { isConnected, isOnline, error, heartbeatStatus, syncStatus } =
    useWebSocketContext();
  const { settings, updateSetting } = useNotificationSettings();
  const [isOpen, setIsOpen] = useState(false);

  const handleUpdateSetting = useCallback(
    (key: keyof NotificationSettings, value: boolean) => {
      if (key === "browserNotification" && value) {
        requestBrowserNotificationPermission().then((granted) => {
          if (granted) {
            updateSetting("browserNotification", true);
          } else {
            toast.message("ブラウザ通知を有効にできません", {
              description: "ブラウザの設定で通知を許可してください。",
            });
          }
        });
        return;
      }
      updateSetting(key, value);
    },
    [updateSetting],
  );
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;
    const handleMouseDown = (e: MouseEvent) => {
      if (!wrapperRef.current?.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setIsOpen(false);
    };
    document.addEventListener("mousedown", handleMouseDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handleMouseDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen]);

  return (
    <WorkspaceHeader
      username={username}
      onLogout={onLogout}
      isConnected={isConnected}
      isOnline={isOnline}
      error={error}
      heartbeatStatus={heartbeatStatus}
      syncStatus={syncStatus}
      isSettingsOpen={isOpen}
      onToggleSettings={() => setIsOpen((v) => !v)}
      settingsRef={wrapperRef}
      settings={settings}
      onUpdateSetting={handleUpdateSetting}
    />
  );
}
