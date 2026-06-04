"use client";

import type { RefObject } from "react";
import { useCallback, useRef } from "react";

interface UseFeedSyncOptions<TFeed extends { sequence_id: number }> {
  fetchFeeds: (afterId: number | null) => Promise<TFeed[]>;
  onFeed: (feed: TFeed) => void;
  syncErrorMessage: string;
}

export function useFeedSync<TFeed extends { sequence_id: number }>(
  isAuthenticated: boolean,
  lastIdRef: RefObject<number | null>,
  setSyncStatus: (value: string) => void,
  { fetchFeeds, onFeed, syncErrorMessage }: UseFeedSyncOptions<TFeed>,
): { fetchMissing: () => Promise<void> } {
  const isSyncingRef = useRef(false);
  const onFeedRef = useRef(onFeed);
  onFeedRef.current = onFeed;
  const fetchFeedsRef = useRef(fetchFeeds);
  fetchFeedsRef.current = fetchFeeds;
  const syncErrorMessageRef = useRef(syncErrorMessage);
  syncErrorMessageRef.current = syncErrorMessage;

  const currentAuthRef = useRef(isAuthenticated);
  currentAuthRef.current = isAuthenticated;

  const fetchMissing = useCallback(async () => {
    if (!currentAuthRef.current || isSyncingRef.current) return;
    isSyncingRef.current = true;
    try {
      const feeds = await fetchFeedsRef.current(lastIdRef.current);
      for (const feed of feeds) {
        onFeedRef.current(feed);
        if (feed.sequence_id > (lastIdRef.current ?? -1)) {
          lastIdRef.current = feed.sequence_id;
        }
      }
      setSyncStatus(`最終同期: ${new Date().toLocaleTimeString()}`);
    } catch (error) {
      // biome-ignore lint/suspicious/noConsole: Error tracking
      console.error("[useFeedSync] Sync error:", error);
      setSyncStatus(syncErrorMessageRef.current);
    } finally {
      isSyncingRef.current = false;
    }
  }, [lastIdRef, setSyncStatus]);

  return { fetchMissing };
}
