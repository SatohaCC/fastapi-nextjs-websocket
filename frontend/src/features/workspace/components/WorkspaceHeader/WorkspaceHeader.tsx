"use client";

import type { NotificationSettings as Settings } from "@/lib/notificationSettings";
import { NotificationSettings } from "../NotificationSettings/NotificationSettings";
import {
  brandGroupStyles,
  gearButtonStyles,
  handleStyles,
  headerStyles,
  logoStyles,
  logoutButtonStyles,
  settingsWrapperStyles,
  statusDotStyles,
  statusIndicatorStyles,
  statusTextStyles,
  systemInfoStyles,
  userGroupStyles,
  userInfoStyles,
  usernameStyles,
} from "./WorkspaceHeader.styles";

interface WorkspaceHeaderProps {
  username: string;
  onLogout: () => void;
  isConnected: boolean;
  isOnline: boolean;
  error: string | null | undefined;
  heartbeatStatus: string;
  syncStatus: string;
  isSettingsOpen: boolean;
  onToggleSettings: () => void;
  settingsRef: { current: HTMLDivElement | null };
  settings: Settings;
  onUpdateSetting: (key: keyof Settings, value: boolean) => void;
}

export function WorkspaceHeader({
  username,
  onLogout,
  isConnected,
  isOnline,
  error,
  heartbeatStatus,
  syncStatus,
  isSettingsOpen,
  onToggleSettings,
  settingsRef,
  settings,
  onUpdateSetting,
}: WorkspaceHeaderProps) {
  const isActuallyConnected = isConnected && isOnline;

  return (
    <header className={headerStyles}>
      <div className={brandGroupStyles}>
        <div className={logoStyles}>WebSocket test</div>
        <output
          className={statusIndicatorStyles}
          aria-live="polite"
          style={{
            background: isActuallyConnected
              ? "#E6F4EA"
              : error
                ? "#FCE8E6"
                : "#FEF3E2",
            borderColor: isActuallyConnected
              ? "#34A853"
              : error
                ? "#D93025"
                : "#E37400",
          }}
        >
          <div
            className={statusDotStyles}
            style={{
              background: isActuallyConnected
                ? "var(--status-completed)"
                : error
                  ? "var(--error)"
                  : "var(--warning)",
            }}
          />
          <span
            className={statusTextStyles}
            style={{
              color: isActuallyConnected
                ? "var(--status-completed)"
                : error
                  ? "var(--error)"
                  : "var(--warning)",
            }}
          >
            {isActuallyConnected
              ? "オンライン"
              : error
                ? "オフライン"
                : "接続中..."}
          </span>
        </output>
        <output
          className={systemInfoStyles}
          aria-live="polite"
          aria-label={`システム情報: 心拍ステータス ${heartbeatStatus}、同期ステータス ${syncStatus}`}
        >
          <span>{heartbeatStatus}</span>
          <span style={{ opacity: 0.3 }}>&bull;</span>
          <span>{syncStatus}</span>
        </output>
      </div>

      <div className={userGroupStyles}>
        <div className={userInfoStyles}>
          <div className={usernameStyles}>{username}</div>
          <div className={handleStyles}>@ {username?.toLowerCase()}</div>
        </div>
        <div ref={settingsRef} className={settingsWrapperStyles}>
          <button
            type="button"
            className={gearButtonStyles}
            onClick={onToggleSettings}
            aria-label="通知設定"
            aria-expanded={isSettingsOpen}
          >
            ⚙
          </button>
          {isSettingsOpen && (
            <NotificationSettings
              settings={settings}
              onUpdate={onUpdateSetting}
            />
          )}
        </div>
        <button type="button" onClick={onLogout} className={logoutButtonStyles}>
          ログアウト
        </button>
      </div>
    </header>
  );
}
