import { useCallback, useRef, useState } from "react";
import { fetchFeeds } from "@/features/websocket/api";
import { mergeById } from "@/features/websocket/utils/mergeById";
import type {
  DirectRequestServerMessage,
  GlobalChatServerMessage,
} from "@/types/ws";

export function useMessageSync(token: string | null) {
  const [chatMessages, setChatMessages] = useState<GlobalChatServerMessage[]>(
    [],
  );
  const [requestMessages, setRequestMessages] = useState<
    DirectRequestServerMessage[]
  >([]);
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
        if (feed.event_type === "global_chat") {
          setChatMessages((prev) =>
            mergeById(prev, [
              {
                ...feed.payload,
                seq: feed.sequence_id,
                is_history: true,
              },
            ]),
          );
        } else if (feed.event_type === "direct_request") {
          setRequestMessages((prev) =>
            mergeById(prev, [
              {
                ...feed.payload,
                seq: feed.sequence_id,
                is_history: true,
              },
            ]),
          );
        } else if (feed.event_type === "direct_request_updated") {
          const payload = feed.payload;
          setRequestMessages((prev) =>
            prev.map((r) =>
              r.id === payload.id
                ? {
                    ...r,
                    ...payload,
                    type: "direct_request" as const,
                    seq: feed.sequence_id,
                  }
                : r,
            ),
          );
        }

        // シーケンスIDの更新
        if (
          feed.sequence_name === "global_chat" &&
          feed.sequence_id > (lastChatId.current ?? -1)
        ) {
          lastChatId.current = feed.sequence_id;
        } else if (
          feed.sequence_name === "direct_request" &&
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
