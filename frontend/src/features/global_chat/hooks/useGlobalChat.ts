"use client";

import { useCallback, useEffect } from "react";
import { useWebSocketContext } from "@/features/common/websocket/context/WebSocketContext";
import { useWsSubscribe } from "@/features/common/websocket/hooks/useWsSubscribe";
import type { GlobalChatServerMessage } from "@/types/ws";
import { sendMessage } from "../api";
import { checkChatSeqGap } from "../handlers/chatSeqGap";
import { handleGlobalChatMessage } from "../handlers/globalChatHandler";
import { useChatSync } from "./useChatSync";
import { useGlobalChatState } from "./useGlobalChatState";

const SYNC_INTERVAL_MS = 30000;

export interface UseGlobalChatResult {
  chatMessages: GlobalChatServerMessage[];
  sendChat: (text: string) => Promise<void>;
}

export function useGlobalChat(token: string | null): UseGlobalChatResult {
  const {
    setSyncStatus,
    setError,
    registerSeqProvider,
    isConnected,
    isOnline,
  } = useWebSocketContext();
  const { chatMessages, setChatMessages, lastChatId } = useGlobalChatState();
  const { fetchChatMissing } = useChatSync(
    token,
    setChatMessages,
    lastChatId,
    setSyncStatus,
  );

  useEffect(
    () => registerSeqProvider("last_chat_id", () => lastChatId.current),
    [registerSeqProvider, lastChatId],
  );

  const handler = useCallback(
    (data: GlobalChatServerMessage) => {
      checkChatSeqGap(data, lastChatId, fetchChatMissing, setSyncStatus);
      handleGlobalChatMessage(data, setChatMessages);
    },
    [lastChatId, fetchChatMissing, setSyncStatus, setChatMessages],
  );
  useWsSubscribe<GlobalChatServerMessage>("global_chat", handler);

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
      } catch {
        setError("メッセージ送信に失敗しました");
      }
    },
    [token, setError],
  );

  return { chatMessages, sendChat };
}
