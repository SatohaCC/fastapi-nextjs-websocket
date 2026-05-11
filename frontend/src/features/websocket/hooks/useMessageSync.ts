import { useCallback, useRef, useState } from "react";
import { fetchFeeds } from "@/features/websocket/api";
import { mergeById } from "@/features/websocket/utils/mergeById";
import type { ChatMessage, RequestMessage } from "@/types/ws";

/**
 * メッセージデータと同期状態を管理するフック
 */
export function useMessageSync(token: string | null) {
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [requestMessages, setRequestMessages] = useState<RequestMessage[]>([]);
  const [syncStatus, setSyncStatus] = useState<string>("未同期");

  // カーソル（最後に受信したID）は再接続時に使用するため、Refで保持する
  const lastChatId = useRef<number | null>(null);
  const lastRequestId = useRef<number | null>(null);

  /**
   * サーバーから欠落しているフィードを取得し、ローカル状態を更新する
   */
  const fetchMissingFeeds = useCallback(async () => {
    if (!token) return;

    try {
      const feeds = await fetchFeeds(
        token,
        lastChatId.current,
        lastRequestId.current,
      );

      setSyncStatus(`最終同期: ${new Date().toLocaleTimeString()}`);

      if (feeds.length === 0) return;

      setChatMessages((prev) => {
        let next = prev;
        for (const feed of feeds) {
          if (feed.event_type === "message") {
            next = mergeById(next, [
              { ...feed.payload, seq: feed.sequence_id, is_history: true },
            ]);
          }
        }
        return next;
      });

      setRequestMessages((prev) => {
        let next = prev;
        for (const feed of feeds) {
          if (feed.event_type === "request") {
            next = mergeById(next, [
              { ...feed.payload, seq: feed.sequence_id, is_history: true },
            ]);
          } else if (feed.event_type === "request_updated") {
            const payload = feed.payload;
            next = next.map((r) =>
              r.id === payload.id
                ? {
                    ...r,
                    ...payload,
                    type: "request" as const,
                    seq: feed.sequence_id,
                  }
                : r,
            );
          }
        }
        return next;
      });

      // シーケンスIDの更新
      for (const feed of feeds) {
        if (
          feed.sequence_name === "chat_global" &&
          feed.sequence_id > (lastChatId.current ?? -1)
        ) {
          lastChatId.current = feed.sequence_id;
        } else if (
          feed.sequence_name === "requests_global" &&
          feed.sequence_id > (lastRequestId.current ?? -1)
        ) {
          lastRequestId.current = feed.sequence_id;
        }
      }

      setSyncStatus(`最終同期: ${new Date().toLocaleTimeString()}`);
    } catch (err) {
      console.error("Failed to fetch missing feeds:", err);
      setSyncStatus("フィード同期失敗");
    }
  }, [token]);

  const clearMessages = useCallback(() => {
    setChatMessages([]);
    setRequestMessages([]);
    lastChatId.current = null;
    lastRequestId.current = null;
    setSyncStatus("クリア済み");
  }, []);

  return {
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
  };
}
