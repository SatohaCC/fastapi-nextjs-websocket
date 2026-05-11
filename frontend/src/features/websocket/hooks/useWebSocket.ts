"use client";

import { useEffect, useState } from "react";
import { dispatchMessage } from "@/features/websocket/handlers";
import { useBackoffRetry } from "./useBackoffRetry";
import { useHeartbeat } from "./useHeartbeat";
import { useMessageSync } from "./useMessageSync";
import { useNetworkStatus } from "./useNetworkStatus";
import { useSocketInstance } from "./useSocketInstance";

/**
 * WebSocket機能のメインオーケストレーター
 */
export function useWebSocket(token: string | null) {
  // 1. データストアと同期ロジック
  const {
    chatMessages,
    setChatMessages,
    requestMessages,
    setRequestMessages,
    syncStatus,
    setSyncStatus,
    lastChatId,
    lastRequestId,
    fetchMissingFeeds,
    clearMessages,
  } = useMessageSync(token);

  // 1.5 ハートビートの表示状態
  const [heartbeatStatus, setHeartbeatStatus] = useState<string>("切断");

  // 2. ネットワーク状態と再試行ロジック
  const isOnline = useNetworkStatus();
  const { recordSuccess, recordFailure } = useBackoffRetry();

  // 3. WebSocket接続インスタンスの先行定義（socketを取得するため）
  // 循環参照を避けるため、ハンドラ内でのみresetHeartbeatを使用する
  const { socket, isConnected, reconnect, disconnect } = useSocketInstance(
    token,
    {
      enabled: isOnline,
      lastChatIdRef: lastChatId,
      lastRequestIdRef: lastRequestId,
      onOpen: () => {
        recordSuccess();
        setSyncStatus("接続済み");
        setHeartbeatStatus("接続中");
      },
      onMessage: (event, socket) => {
        activeResetHeartbeat(); // メッセージ受信時にハートビートをリセット
        dispatchMessage(event, socket, {
          setChatMessages,
          setRequestMessages,
          setError: (msg) => setSyncStatus(`エラー: ${msg}`),
          setSyncStatus,
          setHeartbeatStatus,
          lastChatId,
          lastRequestId,
          resetPingTimeout: activeResetHeartbeat,
          fetchMissingFeeds,
        });
      },
      onClose: () => {
        if (isOnline) {
          const delay = recordFailure();
          const message = `切断されました。${delay / 1000}秒後に再接続します...`;
          setSyncStatus(message);
          setHeartbeatStatus(`再試行待機 (${delay / 1000}s)`);
          setTimeout(reconnect, delay);
        } else {
          setSyncStatus("ネットワークオフライン");
          setHeartbeatStatus("切断");
        }
      },
      onError: () => {
        setSyncStatus((prev) =>
          prev.includes("秒後に再接続") ? prev : "接続エラー",
        );
        setHeartbeatStatus("接続エラー");
      },
    },
  );

  // 4. 死活監視
  const { resetHeartbeat: activeResetHeartbeat } = useHeartbeat(socket, {
    onTimeout: () => {
      setSyncStatus("通信タイムアウト。再接続します...");
      socket?.close();
    },
  });

  // ── ライフサイクル管理 ──

  // トークン変更時に状態をクリア
  useEffect(() => {
    if (token) {
      clearMessages();
    }
  }, [token, clearMessages]);

  // 定期同期（安全策としてのポーリング）
  useEffect(() => {
    const syncInterval = setInterval(() => {
      if (isConnected && isOnline) {
        fetchMissingFeeds();
      }
    }, 30000);
    return () => clearInterval(syncInterval);
  }, [isConnected, isOnline, fetchMissingFeeds]);

  return {
    chatMessages,
    requestMessages,
    isConnected,
    isOnline,
    error: syncStatus.includes("エラー") ? syncStatus : null,
    syncStatus,
    heartbeatStatus,
    disconnect,
  };
}
