"use client";

import { useCallback, useEffect } from "react";
import { useWebSocketContext } from "@/features/common/websocket/context/WebSocketContext";
import { useWsSubscribe } from "@/features/common/websocket/hooks/useWsSubscribe";
import type {
  DirectRequestServerMessage,
  DirectRequestUpdatedServerMessage,
  TaskStatus,
} from "@/types/ws";
import { sendRequest as apiSendRequest, updateRequestStatus } from "../api";
import {
  handleDirectRequestMessage,
  handleDirectRequestUpdated,
} from "../handlers/directRequestHandler";
import { checkRequestSeqGap } from "../handlers/requestSeqGap";
import { useDirectRequestState } from "./useDirectRequestState";
import { useRequestSync } from "./useRequestSync";

const SYNC_INTERVAL_MS = 30000;

export interface UseDirectRequestResult {
  requestMessages: DirectRequestServerMessage[];
  sendRequest: (to: string, text: string) => Promise<void>;
  updateStatus: (taskId: number, status: TaskStatus) => Promise<void>;
}

/**
 * ダイレクトリクエスト機能を提供するカスタムフック。
 *
 * 以下の処理を管理します：
 * - リアルタイムの依頼受信、ステータス変更の通知、およびギャップ検知
 * - 接続成功時（初期接続および再接続時）の即時履歴データ同期
 * - 30秒間隔の定期バックグラウンド同期
 * - リクエストの送信、ステータスの更新、およびエラーハンドリング
 *
 * @param token 認証トークン
 */
export function useDirectRequest(token: string | null): UseDirectRequestResult {
  const {
    setSyncStatus,
    setError,
    registerSeqProvider,
    isConnected,
    isOnline,
  } = useWebSocketContext();
  const { requestMessages, setRequestMessages, lastRequestId } =
    useDirectRequestState();
  const { fetchRequestMissing } = useRequestSync(
    token,
    setRequestMessages,
    lastRequestId,
    setSyncStatus,
  );

  useEffect(
    () => registerSeqProvider("last_request_id", () => lastRequestId.current),
    [registerSeqProvider, lastRequestId],
  );

  const requestHandler = useCallback(
    (data: DirectRequestServerMessage) => {
      checkRequestSeqGap(
        data,
        lastRequestId,
        fetchRequestMissing,
        setSyncStatus,
      );
      handleDirectRequestMessage(data, setRequestMessages);
    },
    [lastRequestId, fetchRequestMissing, setSyncStatus, setRequestMessages],
  );
  useWsSubscribe<DirectRequestServerMessage>("direct_request", requestHandler);

  const updatedHandler = useCallback(
    (data: DirectRequestUpdatedServerMessage) => {
      checkRequestSeqGap(
        data,
        lastRequestId,
        fetchRequestMissing,
        setSyncStatus,
      );
      handleDirectRequestUpdated(data, setRequestMessages);
    },
    [lastRequestId, fetchRequestMissing, setSyncStatus, setRequestMessages],
  );
  useWsSubscribe<DirectRequestUpdatedServerMessage>(
    "direct_request_updated",
    updatedHandler,
  );

  // 接続成功時または再接続時に即時同期をトリガー
  useEffect(() => {
    if (isConnected && isOnline) {
      fetchRequestMissing();
    }
  }, [isConnected, isOnline, fetchRequestMissing]);

  useEffect(() => {
    const interval = setInterval(() => {
      if (isConnected && isOnline && lastRequestId.current !== null) {
        fetchRequestMissing();
      }
    }, SYNC_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [isConnected, isOnline, fetchRequestMissing, lastRequestId]);

  // biome-ignore lint/correctness/useExhaustiveDependencies: token 変更時に履歴と seq をリセットするために依存に含める
  useEffect(() => {
    setRequestMessages([]);
    lastRequestId.current = null;
  }, [token, setRequestMessages, lastRequestId]);

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
    async (taskId: number, status: TaskStatus) => {
      if (!token) return;
      try {
        await updateRequestStatus(token, taskId, status);
      } catch {
        setError("ステータス更新に失敗しました");
      }
    },
    [token, setError],
  );

  return { requestMessages, sendRequest, updateStatus };
}
