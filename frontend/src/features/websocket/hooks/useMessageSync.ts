import { useCallback, useRef, useState } from "react";
import { fetchFeeds } from "@/features/websocket/api";
import { mergeById } from "@/features/websocket/utils/mergeById";
import type { ChatMessage, RequestMessage } from "@/types/ws";

export function useMessageSync(token: string | null) {
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [requestMessages, setRequestMessages] = useState<RequestMessage[]>([]);
  const [syncStatus, setSyncStatus] = useState<string>("未同期");

  const lastChatId = useRef<number | null>(null);
  const lastRequestId = useRef<number | null>(null);

  const fetchMissingFeeds = useCallback(async () => {
    if (!token) return;
    try {
      const feeds = await fetchFeeds(
        token,
        lastChatId.current,
        lastRequestId.current,
      );
      for (const feed of feeds) {
        if (feed.event_type === "message") {
          setChatMessages((prev) =>
            mergeById(prev, [
              {
                ...(feed.payload as ChatMessage),
                seq: feed.sequence_id,
                is_history: true,
              },
            ]),
          );
        } else if (feed.event_type === "request") {
          setRequestMessages((prev) =>
            mergeById(prev, [
              {
                ...(feed.payload as RequestMessage),
                seq: feed.sequence_id,
                is_history: true,
              },
            ]),
          );
        } else if (feed.event_type === "request_updated") {
          const payload = feed.payload as RequestMessage;
          setRequestMessages((prev) =>
            prev.map((r) =>
              r.id === payload.id
                ? { ...r, ...payload, seq: feed.sequence_id }
                : r,
            ),
          );
        }

        // シーケンスIDの更新
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
    } catch {
      setSyncStatus("フィード同期失敗");
    }
  }, [token]);

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
  };
}
