"use client";

import { useCallback, useEffect, useRef } from "react";
import { useWebSocketContext } from "@/features/common/websocket/context/WebSocketContext";
import { checkSeqGap } from "@/features/common/websocket/handlers/seqGap";
import { useWsSubscribe } from "@/features/common/websocket/hooks/useWsSubscribe";
import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import { SYNC_INTERVAL_MS } from "@/lib/config";
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
import { useDirectRequestState } from "./useDirectRequestState";
import { useRequestSync } from "./useRequestSync";

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
  const { username } = useWorkspaceContext();
  const { requestMessages, setRequestMessages, lastRequestId } =
    useDirectRequestState();
  const { fetchRequestMissing } = useRequestSync(
    token,
    setRequestMessages,
    lastRequestId,
    setSyncStatus,
  );

  const pendingResolversRef = useRef<{ text: string; resolve: () => void }[]>(
    [],
  );

  useEffect(
    () => registerSeqProvider("last_request_id", () => lastRequestId.current),
    [registerSeqProvider, lastRequestId],
  );

  const requestHandler = useCallback(
    (data: DirectRequestServerMessage) => {
      checkSeqGap(
        data,
        "direct_request",
        lastRequestId,
        fetchRequestMissing,
        setSyncStatus,
      );
      handleDirectRequestMessage(data, setRequestMessages);

      if (data.sender === username) {
        const resolvers = pendingResolversRef.current;
        const index = resolvers.findIndex((r) => r.text === data.text);
        if (index !== -1) {
          resolvers[index].resolve();
          resolvers.splice(index, 1);
        }
      }
    },
    [
      lastRequestId,
      fetchRequestMissing,
      setSyncStatus,
      setRequestMessages,
      username,
    ],
  );
  useWsSubscribe<DirectRequestServerMessage>("direct_request", requestHandler);

  const updatedHandler = useCallback(
    (data: DirectRequestUpdatedServerMessage) => {
      checkSeqGap(
        data,
        "direct_request",
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

        // オフラインまたは切断時はWebSocketメッセージは届かないため、即時解決して終わる
        if (!isConnected || !isOnline) {
          return;
        }

        // オンライン時はWebSocketからのメッセージ受信を待つ
        await new Promise<void>((resolve) => {
          const timeout = setTimeout(() => {
            const idx = pendingResolversRef.current.findIndex(
              (r) => r.resolve === resolve,
            );
            if (idx !== -1) {
              pendingResolversRef.current.splice(idx, 1);
            }
            resolve();
          }, 5000);

          pendingResolversRef.current.push({
            text,
            resolve: () => {
              clearTimeout(timeout);
              resolve();
            },
          });
        });
      } catch (err) {
        setError("リクエスト送信に失敗しました");
        throw err;
      }
    },
    [token, setError, isConnected, isOnline],
  );

  const updateStatus = useCallback(
    async (taskId: number, status: TaskStatus) => {
      if (!token) return;
      try {
        await updateRequestStatus(token, taskId, status);
      } catch (err) {
        setError("ステータス更新に失敗しました");
        throw err;
      }
    },
    [token, setError],
  );

  return { requestMessages, sendRequest, updateStatus };
}
