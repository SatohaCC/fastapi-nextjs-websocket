"use client";

import { Toggle } from "@/components/ui/Toggle/Toggle";
import type { NotificationSettings as Settings } from "@/lib/notificationSettings";
import {
  settingsListStyles,
  settingsPanelStyles,
  settingsTitleStyles,
} from "./NotificationSettings.styles";

interface NotificationSettingsProps {
  settings: Settings;
  onUpdate: (key: keyof Settings, value: boolean) => void;
}

export function NotificationSettings({
  settings,
  onUpdate,
}: NotificationSettingsProps) {
  return (
    <div className={settingsPanelStyles}>
      <p className={settingsTitleStyles}>通知設定</p>
      <div className={settingsListStyles}>
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
