"use client";

import { useEffect, useState } from "react";
import {
  DEFAULT_SETTINGS,
  type NotificationSettings,
  subscribe,
  updateSetting,
} from "@/lib/notificationSettings";

export function useNotificationSettings() {
  const [settings, setSettings] =
    useState<NotificationSettings>(DEFAULT_SETTINGS);

  useEffect(() => {
    // subscribe immediately calls fn with current (localStorage) value, resolving SSR mismatch
    return subscribe(setSettings);
  }, []);

  return { settings, updateSetting };
}
