"use client";

import { useCallback, useEffect } from "react";
import {
  sendRequest as apiSendRequest,
  sendMessage,
  updateRequestStatus,
} from "@/features/websocket/api";
import { dispatchMessage } from "@/features/websocket/handlers";
import type { RequestStatus } from "@/types/ws";
import { useConnection } from "./useConnection";
import { useMessageSync } from "./useMessageSync";

const INITIAL_RETRY_MS = 1000;

export function useWebSocket(token: string | null) {
  // 1. メッセージ・同期管理のフック
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
  } = useMessageSync(token);

  // 2. 接続管理のフック
  const {
    isConnected,
    isOnline,
    setIsOnline,
    error,
    setError,
    heartbeatStatus,
    setHeartbeatStatus,
    connect,
    disconnect,
    resetPingTimeout,
    retryMsRef,
  } = useConnection({
    token,
    lastChatIdRef: lastChatId,
    lastRequestIdRef: lastRequestId,
    onMessage: (event, socket) => {
      dispatchMessage(event, socket, {
        setChatMessages,
        setRequestMessages,
        setError,
        setSyncStatus,
        setHeartbeatStatus,
        lastChatId,
        lastRequestId,
        resetPingTimeout,
        fetchMissingFeeds,
      });
    },
    onStatusChange: setSyncStatus,
  });

  // 3. API アクション
  const sendChat = useCallback(
    async (text: string) => {
      if (!token) return;
      try {
        await sendMessage(token, text);
      } catch {
        setError("メッセージ送信に失敗しました");
      }
    },
    [token, setError],
  );

  const sendRequest = useCallback(
    async (to: string, text: string) => {
      if (!token) return;
      try {
        await apiSendRequest(token, { to, text });
      } catch {
        setError("リクエスト送信に失敗しました");
      }
    },
    [token, setError],
  );

  const updateStatus = useCallback(
    async (requestId: number, status: RequestStatus) => {
      if (!token) return;
      try {
        await updateRequestStatus(token, requestId, status);
      } catch {
        setError("ステータス更新に失敗しました");
      }
    },
    [token, setError],
  );

  // ── トークン監視 ──
  useEffect(() => {
    // トークンが変わったら、古いデータを即座にクリアする
    setChatMessages([]);
    setRequestMessages([]);
    setSyncStatus("待機中...");

    if (token) {
      disconnect(); // 古い接続があれば掃除
      connect();
    }
  }, [
    token,
    connect,
    disconnect,
    setChatMessages,
    setRequestMessages,
    setSyncStatus,
  ]);

  // ── ネットワーク監視 & 定期同期 ──
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      retryMsRef.current = INITIAL_RETRY_MS;
      setSyncStatus("ネットワーク復帰。再接続しています...");
      connect();
    };
    const handleOffline = () => {
      setIsOnline(false);
      setSyncStatus("ネットワークオフライン");
      disconnect();
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    const syncInterval = setInterval(() => {
      if (isConnected && navigator.onLine) {
        setSyncStatus(`最終同期: ${new Date().toLocaleTimeString()}`);
        if (lastChatId.current !== null || lastRequestId.current !== null) {
          fetchMissingFeeds();
        }
      }
    }, 30000);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
      clearInterval(syncInterval);
    };
  }, [
    isConnected,
    connect,
    disconnect,
    fetchMissingFeeds,
    setSyncStatus,
    setIsOnline,
    retryMsRef,
    lastChatId.current,
    lastRequestId.current,
  ]);

  // ソート済みメッセージの提供
  // seq が無い（履歴）場合は id でソートし、seq がある場合は seq でソートする。
  const sortedChatMessages = [...chatMessages].sort((a, b) => {
    const aSeq = a.seq ?? 0;
    const bSeq = b.seq ?? 0;
    if (aSeq !== bSeq) return aSeq - bSeq;
    return (a.id ?? 0) - (b.id ?? 0);
  });
  const sortedRequestMessages = [...requestMessages].sort((a, b) => {
    const aSeq = a.seq ?? 0;
    const bSeq = b.seq ?? 0;
    if (aSeq !== bSeq) return aSeq - bSeq;
    return (a.id ?? 0) - (b.id ?? 0);
  });

  return {
    chatMessages: sortedChatMessages,
    requestMessages: sortedRequestMessages,
    isConnected,
    isOnline,
    error,
    heartbeatStatus,
    syncStatus,
    connect,
    disconnect,
    sendChat,
    sendRequest,
    updateStatus,
  };
}
