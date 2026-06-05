"use client";

import { useCallback, useEffect, useState } from "react";
import {
  fetchNotificationSettings,
  saveNotificationSettings,
} from "@/features/workspace/api";
import {
  DEFAULT_SETTINGS,
  getSettings,
  initSettings,
  type NotificationSettings,
  subscribe,
  updateSetting,
} from "@/lib/notificationSettings";
import { toast } from "@/lib/toast";

export function useNotificationSettings() {
  const [settings, setSettings] =
    useState<NotificationSettings>(DEFAULT_SETTINGS);

  useEffect(() => {
    fetchNotificationSettings()
      .then(initSettings)
      .catch((err) => {
        // biome-ignore lint/suspicious/noConsole: Error tracking
        console.error("Failed to load notification settings:", err);
      });
    return subscribe(setSettings);
  }, []);

  const handleUpdate = useCallback(
    <K extends keyof NotificationSettings>(key: K, value: boolean) => {
      const previous = getSettings();
      updateSetting(key, value); // optimistic update

      saveNotificationSettings(getSettings()).catch((error) => {
        // biome-ignore lint/suspicious/noConsole: Error tracking
        console.error("[useNotificationSettings] save failed", error);
        // rollback
        updateSetting(key, previous[key]);
        toast.message("エラー", {
          description: "通知設定の保存に失敗しました。",
        });
      });
    },
    [],
  );

  return { settings, updateSetting: handleUpdate };
}
