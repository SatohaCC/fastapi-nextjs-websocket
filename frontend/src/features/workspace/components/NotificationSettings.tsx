"use client";

import { Toggle } from "@/components/ui/Toggle/Toggle";
import type { NotificationSettings as Settings } from "@/lib/notificationSettings";
import styles from "./NotificationSettings.module.css";

interface NotificationSettingsProps {
  settings: Settings;
  onUpdate: (key: keyof Settings, value: boolean) => void;
}

export function NotificationSettings({
  settings,
  onUpdate,
}: NotificationSettingsProps) {
  return (
    <div className={styles.panel}>
      <p className={styles.title}>通知設定</p>
      <div className={styles.list}>
        <Toggle
          checked={settings.globalChat}
          onChange={(v) => onUpdate("globalChat", v)}
          label="グローバルチャット"
        />
        <Toggle
          checked={settings.directRequest}
          onChange={(v) => onUpdate("directRequest", v)}
          label="リクエスト受信"
        />
        <Toggle
          checked={settings.directRequestUpdated}
          onChange={(v) => onUpdate("directRequestUpdated", v)}
          label="ステータス変更"
        />
        <Toggle
          checked={settings.browserNotification}
          onChange={(v) => onUpdate("browserNotification", v)}
          label="ブラウザ通知"
        />
      </div>
    </div>
  );
}
