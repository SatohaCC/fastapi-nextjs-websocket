"use client";

import type { Dispatch, RefObject, SetStateAction } from "react";
import { useCallback } from "react";
import { mergeById } from "@/features/common/websocket/utils/mergeById";
import type { DirectRequestServerMessage } from "@/types/ws";
import { fetchRequestFeeds } from "../api";

export function useRequestSync(
  token: string | null,
  setRequestMessages: Dispatch<SetStateAction<DirectRequestServerMessage[]>>,
  lastRequestId: RefObject<number | null>,
  setSyncStatus: (value: string) => void,
) {
  const fetchRequestMissing = useCallback(async () => {
    if (!token) return;
    try {
      const feeds = await fetchRequestFeeds(token, lastRequestId.current);
      for (const feed of feeds) {
        if (feed.event_type === "direct_request") {
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
        if (feed.sequence_id > (lastRequestId.current ?? -1)) {
          lastRequestId.current = feed.sequence_id;
        }
      }
      setSyncStatus(`最終同期: ${new Date().toLocaleTimeString()}`);
    } catch {
      setSyncStatus("リクエスト同期失敗");
    }
  }, [token, setRequestMessages, lastRequestId, setSyncStatus]);

  return { fetchRequestMissing };
}
