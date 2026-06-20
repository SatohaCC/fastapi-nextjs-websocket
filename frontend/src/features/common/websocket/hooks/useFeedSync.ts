"use client";

import type { RefObject } from "react";
import { useCallback, useRef } from "react";
import { runFeedSync } from "./feedSyncRunner";

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
  // 同期実行中にギャップを検知した場合に立てる保留フラグ。
  // 取りこぼしたギャップ復旧を、現在の同期完了後に必ず再実行するために使う。
  const pendingSyncRef = useRef(false);
  const onFeedRef = useRef(onFeed);
  onFeedRef.current = onFeed;
  const fetchFeedsRef = useRef(fetchFeeds);
  fetchFeedsRef.current = fetchFeeds;
  const syncErrorMessageRef = useRef(syncErrorMessage);
  syncErrorMessageRef.current = syncErrorMessage;

  const currentAuthRef = useRef(isAuthenticated);
  currentAuthRef.current = isAuthenticated;

  const fetchMissing = useCallback(
    () =>
      runFeedSync<TFeed>({
        isSyncingRef,
        pendingSyncRef,
        lastIdRef,
        isAuthenticated: () => currentAuthRef.current,
        fetchFeeds: (afterId) => fetchFeedsRef.current(afterId),
        onFeed: (feed) => onFeedRef.current(feed),
        setSyncStatus,
        syncErrorMessage: syncErrorMessageRef.current,
      }),
    [lastIdRef, setSyncStatus],
  );

  return { fetchMissing };
}
