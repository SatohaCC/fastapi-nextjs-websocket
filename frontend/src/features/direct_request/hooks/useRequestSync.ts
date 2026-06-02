"use client";

import type { Dispatch, RefObject, SetStateAction } from "react";
import { useFeedSync } from "@/features/common/websocket/hooks/useFeedSync";
import { mergeById } from "@/features/common/websocket/utils/mergeById";
import type { DirectRequestServerMessage } from "@/types/ws";
import type { RequestFeedItem } from "../api";
import { fetchRequestFeeds } from "../api";

export function useRequestSync(
  token: string | null,
  setRequestMessages: Dispatch<SetStateAction<DirectRequestServerMessage[]>>,
  lastRequestId: RefObject<number | null>,
  setSyncStatus: (value: string) => void,
) {
  const { fetchMissing: fetchRequestMissing } = useFeedSync<RequestFeedItem>(
    token,
    lastRequestId,
    setSyncStatus,
    {
      fetchFeeds: fetchRequestFeeds,
      onFeed: (feed) => {
        if (feed.event_type === "direct_request_updated") {
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
        } else {
          setRequestMessages((prev) =>
            mergeById(prev, [
              {
                ...feed.payload,
                seq: feed.sequence_id,
                is_history: true,
              },
            ]),
          );
        }
      },
      syncErrorMessage: "リクエスト同期失敗",
    },
  );

  return { fetchRequestMissing };
}
