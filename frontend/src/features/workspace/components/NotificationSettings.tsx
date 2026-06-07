"use client";

import { Toggle } from "@/components/ui/Toggle/Toggle";
import type { NotificationSettings as Settings } from "@/lib/notificationSettings";
import { css } from "@/styled-system/css";

const settingsPanelStyles = css({
  position: "absolute",
  top: "calc(100% + 8px)",
  right: 0,
  background: "rgba(18, 18, 23, 0.97)",
  backdropFilter: "blur(12px) saturate(180%)",
  border: "1px solid rgba(255, 255, 255, 0.1)",
  borderRadius: "12px",
  padding: "16px",
  minWidth: "220px",
  zIndex: 100,
  boxShadow: "0 8px 32px rgba(0, 0, 0, 0.5)",
  animation: "fadeIn 0.15s ease-out",
});

const settingsTitleStyles = css({
  fontSize: "0.8rem",
  fontWeight: 700,
  color: "textSecondary",
  textTransform: "uppercase",
  letterSpacing: "0.06em",
  marginBottom: "12px",
});

const settingsListStyles = css({
  display: "flex",
  flexDirection: "column",
  gap: "12px",
});

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
