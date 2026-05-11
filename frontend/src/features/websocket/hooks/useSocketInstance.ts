"use client";

import type { RefObject } from "react";
import { useCallback, useEffect, useRef, useState } from "react";
import { WS_BASE } from "@/lib/config";

interface Handlers {
  onOpen?: (socket: WebSocket) => void;
  onMessage?: (event: MessageEvent, socket: WebSocket) => void;
  onClose?: (event: CloseEvent) => void;
  onError?: (event: Event) => void;
}

interface Options extends Handlers {
  lastChatIdRef?: RefObject<number | null>;
  lastRequestIdRef?: RefObject<number | null>;
  enabled?: boolean;
}

/**
 * WebSocketインスタンスのライフサイクルを管理するフック
 */
export function useSocketInstance(token: string | null, options: Options = {}) {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const isManualRef = useRef(false);

  const {
    enabled = true,
    lastChatIdRef,
    lastRequestIdRef,
    onOpen,
    onMessage,
    onClose,
    onError,
  } = options;

  // ハンドラを最新のRefに保持し、reconnect関数が頻繁に再生成されるのを防ぐ
  const handlersRef = useRef({ onOpen, onMessage, onClose, onError });
  useEffect(() => {
    handlersRef.current = { onOpen, onMessage, onClose, onError };
  }, [onOpen, onMessage, onClose, onError]);

  const connect = useCallback(() => {
    if (!token || !enabled) return;

    isManualRef.current = false;
    if (wsRef.current) {
      wsRef.current.onclose = null;
      wsRef.current.close();
    }

    const url = new URL(`${WS_BASE}/ws`);
    url.searchParams.set("token", token);
    if (
      lastChatIdRef?.current !== undefined &&
      lastChatIdRef.current !== null
    ) {
      url.searchParams.set("last_chat_id", lastChatIdRef.current.toString());
    }
    if (
      lastRequestIdRef?.current !== undefined &&
      lastRequestIdRef.current !== null
    ) {
      url.searchParams.set(
        "last_request_id",
        lastRequestIdRef.current.toString(),
      );
    }

    const ws = new WebSocket(url.toString());
    wsRef.current = ws;
    setSocket(ws);

    ws.onopen = () => {
      setIsConnected(true);
      handlersRef.current.onOpen?.(ws);
    };

    ws.onmessage = (event) => {
      handlersRef.current.onMessage?.(event, ws);
    };

    ws.onclose = (event) => {
      setIsConnected(false);
      setSocket(null);
      wsRef.current = null;
      if (!isManualRef.current) {
        handlersRef.current.onClose?.(event);
      }
    };

    ws.onerror = (event) => {
      handlersRef.current.onError?.(event);
    };
  }, [token, enabled, lastChatIdRef, lastRequestIdRef]);

  const disconnect = useCallback(() => {
    isManualRef.current = true;
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
    setSocket(null);
  }, []);

  useEffect(() => {
    if (enabled && token) {
      connect();
    }
    return () => {
      if (wsRef.current) {
        wsRef.current.onclose = null;
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [token, enabled, connect]);

  return { socket, isConnected, reconnect: connect, disconnect };
}
