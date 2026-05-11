"use client";

import { useEffect } from "react";
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
      },
      onMessage: (event, socket) => {
        activeResetHeartbeat(); // メッセージ受信時にハートビートをリセット
        dispatchMessage(event, socket, {
          setChatMessages,
          setRequestMessages,
          setError: (msg) => setSyncStatus(`エラー: ${msg}`),
          setSyncStatus,
          setHeartbeatStatus: () => {},
          lastChatId,
          lastRequestId,
          resetPingTimeout: activeResetHeartbeat,
          fetchMissingFeeds,
        });
      },
      onClose: () => {
        if (isOnline) {
          const delay = recordFailure();
          setSyncStatus(`切断されました。${delay / 1000}秒後に再接続します...`);
          setTimeout(reconnect, delay);
        } else {
          setSyncStatus("ネットワークオフライン");
        }
      },
      onError: () => setSyncStatus("接続エラー"),
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
    heartbeatStatus: isConnected ? "接続中" : "切断",
    disconnect,
  };
}
