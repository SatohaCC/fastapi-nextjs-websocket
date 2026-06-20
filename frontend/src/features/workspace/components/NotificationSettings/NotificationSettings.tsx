"use client";

import Link from "next/link";
import { Toggle } from "@/components/ui/primitives";
import type { NotificationSettings as Settings } from "@/lib/notificationSettings";
import { SessionList } from "../SessionList/SessionList";
import {
  dangerLinkStyles,
  linkButtonStyles,
  sectionSeparatorStyles,
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

      <div className={sectionSeparatorStyles} />

      <p className={settingsTitleStyles}>アカウント設定</p>
      <div className={settingsListStyles} style={{ gap: "10px" }}>
        <Link href="/settings/username" className={linkButtonStyles}>
          <span>表示名の変更</span>
          <span>→</span>
        </Link>
        <Link href="/settings/password" className={linkButtonStyles}>
          <span>パスワードの変更</span>
          <span>→</span>
        </Link>
        <Link href="/settings/delete" className={dangerLinkStyles}>
          <span>退会する (アカウント削除)</span>
          <span>→</span>
        </Link>
      </div>

      <div className={sectionSeparatorStyles} />

      <SessionList />
    </div>
  );
}
