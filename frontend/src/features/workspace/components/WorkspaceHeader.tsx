"use client";

import type { NotificationSettings as Settings } from "@/lib/notificationSettings";
import { css } from "@/styled-system/css";
import { NotificationSettings } from "./NotificationSettings";

const headerStyles = css({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  padding: "12px 16px",
  borderBottom: "1px solid",
  borderColor: "panelBorder",
  background: "rgba(0, 0, 0, 0.6)",
  backdropFilter: "blur(20px) saturate(150%)",
  position: "sticky",
  top: 0,
  zIndex: 10,
  borderRadius: "0 0 16px 16px",
  boxShadow: "0 4px 30px rgba(0, 0, 0, 0.5)",
  "@media (max-width: 1024px)": {
    flexDirection: "column",
    gap: "16px",
    alignItems: "flex-start",
  },
});

const brandGroupStyles = css({
  display: "flex",
  alignItems: "center",
  gap: "12px",
});

const logoStyles = css({
  fontSize: "28px",
  fontWeight: 900,
  color: "white",
  letterSpacing: "-0.05em",
});

const statusIndicatorStyles = css({
  display: "flex",
  alignItems: "center",
  gap: "6px",
  fontSize: "13px",
  padding: "4px 12px",
  borderRadius: "99px",
  border: "1px solid transparent",
});

const statusDotStyles = css({
  width: "6px",
  height: "6px",
  borderRadius: "50%",
});

const statusTextStyles = css({
  fontWeight: 700,
});

const systemInfoStyles = css({
  fontSize: "13px",
  color: "rgba(255, 255, 255, 0.6)",
  marginLeft: "16px",
  fontFamily: "monospace",
  textTransform: "uppercase",
  letterSpacing: "0.05em",
  display: "flex",
  gap: "16px",
});

const userGroupStyles = css({
  display: "flex",
  alignItems: "center",
  gap: "24px",
  "@media (max-width: 1024px)": {
    width: "100%",
    justifyContent: "space-between",
  },
});

const userInfoStyles = css({
  textAlign: "right",
});

const usernameStyles = css({
  fontSize: "16px",
  color: "white",
  fontWeight: 800,
});

const handleStyles = css({
  fontSize: "13px",
  color: "textSecondary",
});

const gearButtonStyles = css({
  background: "none",
  border: "none",
  cursor: "pointer",
  fontSize: "18px",
  color: "textSecondary",
  padding: "4px",
  borderRadius: "50%",
  lineHeight: 1,
  transition: "color 0.15s",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  _hover: {
    color: "textPrimary",
  },
});

const settingsWrapperStyles = css({
  position: "relative",
});

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
