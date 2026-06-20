"use client";

import { useCallback, useEffect, useRef } from "react";
import { useWebSocketContext } from "@/features/common/websocket/context/WebSocketContext";
import { checkSeqGap } from "@/features/common/websocket/handlers/seqGap";
import { useWsSubscribe } from "@/features/common/websocket/hooks/useWsSubscribe";
import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import { SYNC_INTERVAL_MS } from "@/lib/config";
import type { GlobalChatServerMessage } from "@/types/ws";
import { fetchChatMessages, sendMessage } from "../api";
import { handleGlobalChatMessage } from "../handlers/globalChatHandler";
import { useChatSync } from "./useChatSync";
import { useGlobalChatState } from "./useGlobalChatState";

export interface UseGlobalChatResult {
  chatMessages: GlobalChatServerMessage[];
  sendChat: (text: string) => Promise<void>;
  fetchPastMessages: () => Promise<void>;
  isFetchingPast: boolean;
  hasMorePast: boolean;
}

/**
 * グローバルチャット機能を提供するカスタムフック。
 *
 * 以下の処理を管理します：
 * - リアルタイムのメッセージ受信およびギャップ（ロスト）検知
 * - 接続成功時（初期接続および再接続時）の即時履歴データ同期
 * - 30秒間隔の定期バックグラウンド同期
 * - メッセージの送信処理とエラーハンドリング
 *
 * @param isAuthenticated 認証状態フラグ
 */
export function useGlobalChat(isAuthenticated: boolean): UseGlobalChatResult {
  const {
    setSyncStatus,
    setError,
    registerSeqProvider,
    isConnected,
    isOnline,
  } = useWebSocketContext();
  const { id } = useWorkspaceContext();
  const {
    chatMessages,
    setChatMessages,
    isFetchingPast,
    setIsFetchingPast,
    hasMorePast,
    setHasMorePast,
    lastChatId,
  } = useGlobalChatState();
  const { fetchChatMissing } = useChatSync(
    isAuthenticated,
    setChatMessages,
    lastChatId,
    setSyncStatus,
  );

  const pendingResolversRef = useRef<{ text: string; resolve: () => void }[]>(
    [],
  );

  useEffect(
    () => registerSeqProvider("last_chat_id", () => lastChatId.current),
    [registerSeqProvider, lastChatId],
  );

  const handler = useCallback(
    (data: GlobalChatServerMessage) => {
      checkSeqGap(
        data,
        "global_chat",
        lastChatId,
        fetchChatMissing,
        setSyncStatus,
      );
      handleGlobalChatMessage(data, setChatMessages);

      if (data.sender_id === id) {
        const resolvers = pendingResolversRef.current;
        const index = resolvers.findIndex((r) => r.text === data.text);
        if (index !== -1) {
          resolvers[index].resolve();
          resolvers.splice(index, 1);
        }
      }
    },
    [lastChatId, fetchChatMissing, setSyncStatus, setChatMessages, id],
  );
  useWsSubscribe<GlobalChatServerMessage>("global_chat", handler);

  // 接続成功時または再接続時に即時同期をトリガー
  useEffect(() => {
    if (isConnected && isOnline) {
      fetchChatMissing();
    }
  }, [isConnected, isOnline, fetchChatMissing]);

  useEffect(() => {
    const interval = setInterval(() => {
      if (isConnected && isOnline && lastChatId.current !== null) {
        fetchChatMissing();
      }
    }, SYNC_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [isConnected, isOnline, fetchChatMissing, lastChatId]);

  const isFirstMount = useRef(true);
  // biome-ignore lint/correctness/useExhaustiveDependencies: isAuthenticated 変更時に履歴と seq をリセットするために依存に含める
  useEffect(() => {
    if (isFirstMount.current) {
      isFirstMount.current = false;
      return;
    }
    setChatMessages([]);
    lastChatId.current = null;
  }, [isAuthenticated, setChatMessages, lastChatId]);

  const sendChat = useCallback(
    async (text: string) => {
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

        await sendMessage(text);

        if (promise) {
          await promise;
        }
      } catch (err) {
        setError("メッセージ送信に失敗しました");
        throw err;
      }
    },
    [isAuthenticated, setError, isConnected, isOnline],
  );

  const fetchPastMessages = useCallback(async () => {
    if (isFetchingPast || !hasMorePast) return;
    if (chatMessages.length === 0) return;

    const oldestId = Math.min(
      ...chatMessages
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
      const pastMessages = await fetchChatMessages({
        before_id: oldestId,
        limit,
      });

      if (pastMessages.length < limit) {
        setHasMorePast(false);
      }

      if (pastMessages.length > 0) {
        const historyMessages = pastMessages.map((m) => ({
          ...m,
          is_history: true,
        }));
        setChatMessages((prev) => {
          const existingIds = new Set(prev.map((m) => m.id));
          const newUnique = historyMessages.filter(
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
      console.error("[fetchPastMessages] Error:", err);
    } finally {
      setIsFetchingPast(false);
    }
  }, [
    chatMessages,
    isFetchingPast,
    hasMorePast,
    setChatMessages,
    setError,
    setIsFetchingPast,
    setHasMorePast,
  ]);

  return {
    chatMessages,
    sendChat,
    fetchPastMessages,
    isFetchingPast,
    hasMorePast,
  };
}
