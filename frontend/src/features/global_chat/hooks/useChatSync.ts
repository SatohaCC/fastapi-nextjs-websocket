"use client";

import type { Dispatch, RefObject, SetStateAction } from "react";
import { useFeedSync } from "@/features/common/websocket/hooks/useFeedSync";
import { mergeById } from "@/features/common/websocket/utils/mergeById";
import type { GlobalChatServerMessage } from "@/types/ws";
import type { ChatFeedItem } from "../api";
import { fetchChatFeeds } from "../api";

export function useChatSync(
  isAuthenticated: boolean,
  setChatMessages: Dispatch<SetStateAction<GlobalChatServerMessage[]>>,
  lastChatId: RefObject<number | null>,
  setSyncStatus: (value: string) => void,
) {
  const { fetchMissing: fetchChatMissing } = useFeedSync<ChatFeedItem>(
    isAuthenticated,
    lastChatId,
    setSyncStatus,
    {
      fetchFeeds: (afterId) => fetchChatFeeds(afterId),
      onFeed: (feed) => {
        setChatMessages((prev) =>
          mergeById(prev, [
            {
              ...feed.payload,
              seq: feed.sequence_id,
              is_history: true,
            },
          ]),
        );
      },
      syncErrorMessage: "チャット同期失敗",
    },
  );

  return { fetchChatMissing };
}
