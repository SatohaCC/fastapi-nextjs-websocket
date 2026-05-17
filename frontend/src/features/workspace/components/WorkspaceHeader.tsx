"use client";

import { useWebSocketContext } from "@/features/common/websocket/context/WebSocketContext";
import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import styles from "./WorkspaceHeader.module.css";

export function WorkspaceHeader() {
  const { username, onLogout } = useWorkspaceContext();
  const { isConnected, isOnline, error, heartbeatStatus, syncStatus } =
    useWebSocketContext();

  const isActuallyConnected = isConnected && isOnline;

  return (
    <header className={styles.header}>
      <div className={styles.brandGroup}>
        <div className={styles.logo}>WebSocket test</div>
        <div
          className={styles.statusIndicator}
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
        </div>
        <div className={styles.systemInfo}>
          <span>{heartbeatStatus}</span>
          <span style={{ opacity: 0.3 }}>&bull;</span>
          <span>{syncStatus}</span>
        </div>
      </div>

      <div className={styles.userGroup}>
        <div className={styles.userInfo}>
          <div className={styles.username}>{username}</div>
          <div className={styles.handle}>@{username?.toLowerCase()}</div>
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
