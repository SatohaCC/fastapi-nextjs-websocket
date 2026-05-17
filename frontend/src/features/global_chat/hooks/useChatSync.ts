"use client";

import type { Dispatch, RefObject, SetStateAction } from "react";
import { useCallback } from "react";
import { mergeById } from "@/features/common/websocket/utils/mergeById";
import type { GlobalChatServerMessage } from "@/types/ws";
import { fetchChatFeeds } from "../api";

export function useChatSync(
  token: string | null,
  setChatMessages: Dispatch<SetStateAction<GlobalChatServerMessage[]>>,
  lastChatId: RefObject<number | null>,
  setSyncStatus: (value: string) => void,
) {
  const fetchChatMissing = useCallback(async () => {
    if (!token) return;
    try {
      const feeds = await fetchChatFeeds(token, lastChatId.current);
      for (const feed of feeds) {
        setChatMessages((prev) =>
          mergeById(prev, [
            {
              ...feed.payload,
              seq: feed.sequence_id,
              is_history: true,
            },
          ]),
        );
        if (feed.sequence_id > (lastChatId.current ?? -1)) {
          lastChatId.current = feed.sequence_id;
        }
      }
      setSyncStatus(`最終同期: ${new Date().toLocaleTimeString()}`);
    } catch {
      setSyncStatus("チャット同期失敗");
    }
  }, [token, setChatMessages, lastChatId, setSyncStatus]);

  return { fetchChatMissing };
}
