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
import {
  sendRequest as apiSendRequest,
  fetchDirectRequests,
  updateRequestStatus,
} from "../api";
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
  fetchPastRequests: () => Promise<void>;
  isFetchingPast: boolean;
  hasMorePast: boolean;
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
 * @param isAuthenticated 認証状態フラグ
 */
export function useDirectRequest(
  isAuthenticated: boolean,
): UseDirectRequestResult {
  const {
    setSyncStatus,
    setError,
    registerSeqProvider,
    isConnected,
    isOnline,
  } = useWebSocketContext();
  const { id } = useWorkspaceContext();
  const {
    requestMessages,
    setRequestMessages,
    isFetchingPast,
    setIsFetchingPast,
    hasMorePast,
    setHasMorePast,
    lastRequestId,
  } = useDirectRequestState();
  const { fetchRequestMissing } = useRequestSync(
    isAuthenticated,
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

      if (data.sender_id === id) {
        const resolvers = pendingResolversRef.current;
        const index = resolvers.findIndex((r) => r.text === data.text);
        if (index !== -1) {
          resolvers[index].resolve();
          resolvers.splice(index, 1);
        }
      }
    },
    [lastRequestId, fetchRequestMissing, setSyncStatus, setRequestMessages, id],
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

  const isFirstMount = useRef(true);
  // biome-ignore lint/correctness/useExhaustiveDependencies: isAuthenticated 変更時に履歴と seq をリセットするために依存に含める
  useEffect(() => {
    if (isFirstMount.current) {
      isFirstMount.current = false;
      return;
    }
    setRequestMessages([]);
    lastRequestId.current = null;
  }, [isAuthenticated, setRequestMessages, lastRequestId]);

  const sendRequest = useCallback(
    async (to: string, text: string) => {
      if (!isAuthenticated) return;
      try {
        let promise: Promise<void> | null = null;
        if (isConnected && isOnline) {
          promise = new Promise<void>((promiseResolve) => {
            let resolverObj: { text: string; resolve: () => void };

            const timeout = setTimeout(() => {
              const idx = pendingResolversRef.current.indexOf(resolverObj);
              if (idx !== -1) {
                pendingResolversRef.current.splice(idx, 1);
              }
              promiseResolve();
            }, 5000);

            resolverObj = {
              text,
              resolve: () => {
                clearTimeout(timeout);
                promiseResolve();
              },
            };

            pendingResolversRef.current.push(resolverObj);
          });
        }

        await apiSendRequest({ to, text });

        if (promise) {
          await promise;
        }
      } catch (err) {
        setError("リクエスト送信に失敗しました");
        throw err;
      }
    },
    [isAuthenticated, setError, isConnected, isOnline],
  );

  const updateStatus = useCallback(
    async (taskId: number, status: TaskStatus) => {
      if (!isAuthenticated) return;
      try {
        await updateRequestStatus(taskId, status);
      } catch (err) {
        setError("ステータス更新に失敗しました");
        throw err;
      }
    },
    [isAuthenticated, setError],
  );

  const fetchPastRequests = useCallback(async () => {
    if (isFetchingPast || !hasMorePast) return;
    if (requestMessages.length === 0) return;

    const oldestId = Math.min(
      ...requestMessages
        .map((m) => m.id)
        .filter((id): id is number => id !== undefined && id !== null),
    );
    if (
      oldestId === Number.POSITIVE_INFINITY ||
      oldestId === Number.NEGATIVE_INFINITY
    )
      return;

    setIsFetchingPast(true);
    try {
      const limit = 50;
      const pastRequests = await fetchDirectRequests({
        before_id: oldestId,
        limit,
      });

      if (pastRequests.length < limit) {
        setHasMorePast(false);
      }

      if (pastRequests.length > 0) {
        const historyRequests = pastRequests.map((m) => ({
          ...m,
          is_history: true,
        }));
        setRequestMessages((prev) => {
          const existingIds = new Set(prev.map((m) => m.id));
          const newUnique = historyRequests.filter(
            (m) => !existingIds.has(m.id),
          );
          return [...newUnique, ...prev];
        });
      } else {
        setHasMorePast(false);
      }
    } catch (err) {
      setError("過去のメッセージ取得に失敗しました");
      // biome-ignore lint/suspicious/noConsole: Error tracking
      console.error("[fetchPastRequests] Error:", err);
    } finally {
      setIsFetchingPast(false);
    }
  }, [
    requestMessages,
    isFetchingPast,
    hasMorePast,
    setRequestMessages,
    setError,
    setIsFetchingPast,
    setHasMorePast,
  ]);

  return {
    requestMessages,
    sendRequest,
    updateStatus,
    fetchPastRequests,
    isFetchingPast,
    hasMorePast,
  };
}
