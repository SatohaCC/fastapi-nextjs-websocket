"use client";

import type { NotificationSettings as Settings } from "@/lib/notificationSettings";
import { NotificationSettings } from "./NotificationSettings";
import notifStyles from "./NotificationSettings.module.css";
import styles from "./WorkspaceHeader.module.css";

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
    <header className={styles.header}>
      <div className={styles.brandGroup}>
        <div className={styles.logo}>WebSocket test</div>
        <output
          className={styles.statusIndicator}
          aria-live="polite"
          style={{
            background: isActuallyConnected
              ? "rgba(0, 186, 124, 0.1)"
              : error
                ? "rgba(244, 33, 46, 0.1)"
                : "rgba(255, 212, 0, 0.1)",
            borderColor: isActuallyConnected
              ? "rgba(0, 186, 124, 0.2)"
              : error
                ? "rgba(244, 33, 46, 0.2)"
                : "rgba(255, 212, 0, 0.2)",
          }}
        >
          <div
            className={styles.statusDot}
            style={{
              background: isActuallyConnected
                ? "var(--status-completed)"
                : error
                  ? "var(--error)"
                  : "var(--warning)",
            }}
          />
          <span
            className={styles.statusText}
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
          className={styles.systemInfo}
          aria-live="polite"
          aria-label={`システム情報: 心拍ステータス ${heartbeatStatus}、同期ステータス ${syncStatus}`}
        >
          <span>{heartbeatStatus}</span>
          <span style={{ opacity: 0.3 }}>&bull;</span>
          <span>{syncStatus}</span>
        </output>
      </div>

      <div className={styles.userGroup}>
        <div className={styles.userInfo}>
          <div className={styles.username}>{username}</div>
          <div className={styles.handle}>@{username?.toLowerCase()}</div>
        </div>
        <div ref={settingsRef} className={notifStyles.wrapper}>
          <button
            type="button"
            className={notifStyles.gearButton}
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
        <button
          type="button"
          onClick={onLogout}
          className="btn-secondary"
          style={{ padding: "8px 20px", fontSize: "14px" }}
        >
          ログアウト
        </button>
      </div>
    </header>
  );
}
