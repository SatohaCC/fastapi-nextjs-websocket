"use client";

import { useEffect } from "react";
import {
  useWebSocketContext,
  type WsHandler,
} from "../context/WebSocketContext";

/**
 * 指定したメッセージタイプの handler を WebSocketProvider に登録する。
 * unmount 時に自動で解除される。handler は呼び出し側で安定化（useCallback）すること。
 */
export function useWsSubscribe<T = unknown>(
  type: string,
  handler: WsHandler<T>,
): void {
  const { subscribe } = useWebSocketContext();
  useEffect(() => {
    const unsubscribe = subscribe(type, handler as WsHandler);
    return unsubscribe;
  }, [subscribe, type, handler]);
}
