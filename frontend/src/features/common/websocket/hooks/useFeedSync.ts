"use client";

import type { RefObject } from "react";
import { useCallback, useRef } from "react";

interface UseFeedSyncOptions<TFeed extends { sequence_id: number }> {
  fetchFeeds: (token: string, afterId: number | null) => Promise<TFeed[]>;
  onFeed: (feed: TFeed) => void;
  syncErrorMessage: string;
}

export function useFeedSync<TFeed extends { sequence_id: number }>(
  token: string | null,
  lastIdRef: RefObject<number | null>,
  setSyncStatus: (value: string) => void,
  { fetchFeeds, onFeed, syncErrorMessage }: UseFeedSyncOptions<TFeed>,
): { fetchMissing: () => Promise<void> } {
  const isSyncingRef = useRef(false);
  // コールバック・設定値はすべて ref 経由で参照し、fetchMissing の参照を安定させる
  const onFeedRef = useRef(onFeed);
  onFeedRef.current = onFeed;
  const fetchFeedsRef = useRef(fetchFeeds);
  fetchFeedsRef.current = fetchFeeds;
  const syncErrorMessageRef = useRef(syncErrorMessage);
  syncErrorMessageRef.current = syncErrorMessage;

  const fetchMissing = useCallback(async () => {
    if (!token || isSyncingRef.current) return;
    isSyncingRef.current = true;
    try {
      const feeds = await fetchFeedsRef.current(token, lastIdRef.current);
      for (const feed of feeds) {
        onFeedRef.current(feed);
        if (feed.sequence_id > (lastIdRef.current ?? -1)) {
          lastIdRef.current = feed.sequence_id;
        }
      }
      setSyncStatus(`最終同期: ${new Date().toLocaleTimeString()}`);
    } catch {
      setSyncStatus(syncErrorMessageRef.current);
    } finally {
      isSyncingRef.current = false;
    }
  }, [token, lastIdRef, setSyncStatus]);

  return { fetchMissing };
}
