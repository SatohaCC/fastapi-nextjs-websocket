"use client";

import { useCallback, useEffect, useRef } from "react";

const DEFAULT_PING_TIMEOUT_MS = (10 + 5 + 2) * 1000;

interface Options {
  onTimeout?: () => void;
  timeoutMs?: number;
}

/**
 * WebSocketの死活監視（Heartbeat）を管理するフック
 */
export function useHeartbeat(socket: WebSocket | null, options: Options = {}) {
  const { onTimeout, timeoutMs = DEFAULT_PING_TIMEOUT_MS } = options;
  const pingTimerRef = useRef<NodeJS.Timeout | null>(null);
  const onTimeoutRef = useRef(onTimeout);

  // ハンドラを最新の状態に保つ
  useEffect(() => {
    onTimeoutRef.current = onTimeout;
  }, [onTimeout]);

  const clearTimer = useCallback(() => {
    if (pingTimerRef.current) {
      clearTimeout(pingTimerRef.current);
      pingTimerRef.current = null;
    }
  }, []);

  const resetTimer = useCallback(() => {
    clearTimer();
    if (socket && socket.readyState === WebSocket.OPEN) {
      pingTimerRef.current = setTimeout(() => {
        onTimeoutRef.current?.();
      }, timeoutMs);
    }
  }, [socket, timeoutMs, clearTimer]);

  // ソケットがオープンな時のみタイマーをセット
  useEffect(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      resetTimer();
    } else {
      clearTimer();
    }
    return () => clearTimer();
  }, [socket, resetTimer, clearTimer]);

  return { resetHeartbeat: resetTimer };
}
