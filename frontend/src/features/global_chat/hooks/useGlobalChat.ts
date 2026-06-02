"use client";

import { useCallback, useEffect, useRef } from "react";
import { useWebSocketContext } from "@/features/common/websocket/context/WebSocketContext";
import { checkSeqGap } from "@/features/common/websocket/handlers/seqGap";
import { useWsSubscribe } from "@/features/common/websocket/hooks/useWsSubscribe";
import { useWorkspaceContext } from "@/features/workspace/context/WorkspaceContext";
import { SYNC_INTERVAL_MS } from "@/lib/config";
import type { GlobalChatServerMessage } from "@/types/ws";
import { sendMessage } from "../api";
import { handleGlobalChatMessage } from "../handlers/globalChatHandler";
import { useChatSync } from "./useChatSync";
import { useGlobalChatState } from "./useGlobalChatState";

export interface UseGlobalChatResult {
  chatMessages: GlobalChatServerMessage[];
  sendChat: (text: string) => Promise<void>;
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
 * @param token 認証トークン
 */
export function useGlobalChat(token: string | null): UseGlobalChatResult {
  const {
    setSyncStatus,
    setError,
    registerSeqProvider,
    isConnected,
    isOnline,
  } = useWebSocketContext();
  const { username } = useWorkspaceContext();
  const { chatMessages, setChatMessages, lastChatId } = useGlobalChatState();
  const { fetchChatMissing } = useChatSync(
    token,
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

      if (data.username === username) {
        const resolvers = pendingResolversRef.current;
        const index = resolvers.findIndex((r) => r.text === data.text);
        if (index !== -1) {
          resolvers[index].resolve();
          resolvers.splice(index, 1);
        }
      }
    },
    [lastChatId, fetchChatMissing, setSyncStatus, setChatMessages, username],
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

  // biome-ignore lint/correctness/useExhaustiveDependencies: token 変更時に履歴と seq をリセットするために依存に含める
  useEffect(() => {
    setChatMessages([]);
    lastChatId.current = null;
  }, [token, setChatMessages, lastChatId]);

  const sendChat = useCallback(
    async (text: string) => {
      if (!token) return;
      try {
        await sendMessage(token, text);

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
        setError("メッセージ送信に失敗しました");
        throw err;
      }
    },
    [token, setError, isConnected, isOnline],
  );

  return { chatMessages, sendChat };
}
