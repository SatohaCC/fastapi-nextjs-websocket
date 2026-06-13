"use client";

import { useEffect, useRef } from "react";
import {
  useWebSocketContext,
  type WsHandler,
} from "../context/WebSocketContext";

/**
 * 指定したメッセージタイプの handler を WebSocketProvider に登録する。
 * unmount 時に自動で解除される。
 *
 * handler は ref 経由で常に最新版を呼ぶため、呼び出し側で useCallback による
 * 安定化は不要。これにより handler の同一性が変わるたびに購読を張り替える
 * チャーン（および張り替え中のメッセージ取りこぼし）を防ぐ。購読は type
 * （と subscribe）が変わったときだけ張り直す。
 */
export function useWsSubscribe<T = unknown>(
  type: string,
  handler: WsHandler<T>,
): void {
  const { subscribe } = useWebSocketContext();
  const handlerRef = useRef(handler);
  handlerRef.current = handler;

  useEffect(() => {
    const stableHandler: WsHandler = (data, socket) => {
      (handlerRef.current as WsHandler)(data, socket);
    };
    const unsubscribe = subscribe(type, stableHandler);
    return unsubscribe;
  }, [subscribe, type]);
}
