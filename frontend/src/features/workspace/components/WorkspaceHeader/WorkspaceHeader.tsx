"use client";

import Link from "next/link";
import {
  brandGroupStyles,
  gearButtonStyles,
  headerStyles,
  logoStyles,
  logoutButtonStyles,
  settingsWrapperStyles,
  statusDotStyles,
  statusIndicatorStyles,
  systemInfoStyles,
  userGroupStyles,
  userInfoStyles,
  usernameStyles,
} from "./WorkspaceHeader.styles";

interface WorkspaceHeaderProps {
  userid: string;
  username: string;
  onLogout: () => void;
  isConnected: boolean;
  isOnline: boolean;
  error: string | null | undefined;
  heartbeatStatus: string;
  syncStatus: string;
  onNavigateToSettings: () => void;
}

export function WorkspaceHeader({
  userid,
  username,
  onLogout,
  isConnected,
  isOnline,
  error,
  heartbeatStatus,
  syncStatus,
  onNavigateToSettings,
}: WorkspaceHeaderProps) {
  const isActuallyConnected = isConnected && isOnline;

  return (
    <header className={headerStyles}>
      <div className={brandGroupStyles}>
        <Link href="/workspace" className={logoStyles}>
          WebSocket test
        </Link>
        <output
          className={statusIndicatorStyles({
            status: isActuallyConnected
              ? "online"
              : error
                ? "offline"
                : "connecting",
          })}
          aria-live="polite"
        >
          <div
            className={statusDotStyles({
              status: isActuallyConnected
                ? "online"
                : error
                  ? "offline"
                  : "connecting",
            })}
          />
          <span>
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
          <div className={usernameStyles}>
            {username}{" "}
            <span style={{ fontSize: "12px", opacity: 0.6 }}>@{userid}</span>
          </div>
        </div>
        <div className={settingsWrapperStyles}>
          <button
            type="button"
            className={gearButtonStyles}
            onClick={onNavigateToSettings}
            aria-label="設定"
          >
            ⚙
          </button>
        </div>
        <button type="button" onClick={onLogout} className={logoutButtonStyles}>
          ログアウト
        </button>
      </div>
    </header>
  );
}
