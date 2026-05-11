"use client";

import { useCallback, useRef, useState } from "react";

interface Options {
  initialDelay?: number;
  maxDelay?: number;
}

/**
 * 指数バックオフによる再試行待ち時間を管理するフック
 */
export function useBackoffRetry({
  initialDelay = 1000,
  maxDelay = 30000,
}: Options = {}) {
  const [currentDelay, setCurrentDelay] = useState(initialDelay);
  const nextDelayRef = useRef(initialDelay);

  const recordSuccess = useCallback(() => {
    nextDelayRef.current = initialDelay;
    setCurrentDelay(initialDelay);
  }, [initialDelay]);

  const recordFailure = useCallback(() => {
    const delayToUse = nextDelayRef.current;
    const next = Math.min(delayToUse * 2, maxDelay);
    nextDelayRef.current = next;
    setCurrentDelay(delayToUse);
    return delayToUse;
  }, [maxDelay]);

  return {
    currentDelay,
    recordSuccess,
    recordFailure,
  };
}
