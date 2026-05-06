import type { RefObject } from "react";
import { useCallback, useEffect, useRef, useState } from "react";
import { WS_BASE } from "@/lib/config";

const PING_TIMEOUT_MS = (10 + 5 + 2) * 1000;
const INITIAL_RETRY_MS = 1000;
const MAX_RETRY_MS = 30000;

interface UseConnectionProps {
  token: string | null;
  lastChatIdRef: RefObject<number | null>;
  lastRequestIdRef: RefObject<number | null>;
  onMessage: (event: MessageEvent, socket: WebSocket) => void;
  onStatusChange?: (status: string) => void;
}

export function useConnection({
  token,
  lastChatIdRef,
  lastRequestIdRef,
  onMessage,
  onStatusChange,
}: UseConnectionProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [heartbeatStatus, setHeartbeatStatus] = useState<string>("待機中");
  const [isOnline, setIsOnline] = useState<boolean>(true);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<NodeJS.Timeout | null>(null);
  const retryMsRef = useRef<number>(INITIAL_RETRY_MS);
  const pingTimerRef = useRef<NodeJS.Timeout | null>(null);
  const isManualRef = useRef(false);

  // トークンの最新値を常にRefに同期 (レンダリングパスで同期して最新を保証)
  const currentTokenRef = useRef<string | null>(token);
  currentTokenRef.current = token;

  const onMessageRef = useRef(onMessage);
  const onStatusChangeRef = useRef(onStatusChange);

  useEffect(() => {
    onMessageRef.current = onMessage;
    onStatusChangeRef.current = onStatusChange;
  }, [onMessage, onStatusChange]);

  const clearPingTimeout = useCallback(() => {
    if (pingTimerRef.current) {
      clearTimeout(pingTimerRef.current);
      pingTimerRef.current = null;
    }
  }, []);

  const resetPingTimeout = useCallback(
    (socket: WebSocket) => {
      clearPingTimeout();
      pingTimerRef.current = setTimeout(() => {
        onStatusChangeRef.current?.("タイムアウトしました。再接続中...");
        socket.close();
      }, PING_TIMEOUT_MS);
    },
    [clearPingTimeout],
  );

  const connectWs = useCallback(() => {
    const activeToken = currentTokenRef.current;
    if (!activeToken) return;

    if (wsRef.current) {
      wsRef.current.onclose = null;
      wsRef.current.close();
      wsRef.current = null;
    }

    const url = new URL(`${WS_BASE}/ws`);
    url.searchParams.set("token", activeToken);
    if (lastChatIdRef.current !== null)
      url.searchParams.set("last_chat_id", lastChatIdRef.current.toString());
    if (lastRequestIdRef.current !== null)
      url.searchParams.set(
        "last_request_id",
        lastRequestIdRef.current.toString(),
      );

    const socket = new WebSocket(url.toString());
    wsRef.current = socket;

    socket.onopen = () => {
      setIsConnected(true);
      setError(null);
      retryMsRef.current = INITIAL_RETRY_MS;
      resetPingTimeout(socket);
      setHeartbeatStatus(`接続済み: ${new Date().toLocaleTimeString()}`);
    };

    socket.onmessage = (event) => onMessageRef.current(event, socket);

    socket.onclose = () => {
      if (wsRef.current !== socket) return;
      setIsConnected(false);
      wsRef.current = null;
      clearPingTimeout();
      if (!isManualRef.current) {
        const delay = retryMsRef.current;
        retryMsRef.current = Math.min(delay * 2, MAX_RETRY_MS);
        onStatusChangeRef.current?.(
          `切断されました。${delay / 1000}秒後に再試行します...`,
        );
        reconnectTimerRef.current = setTimeout(connectWs, delay);
      }
    };

    socket.onerror = () => {
      setError("WebSocket connection error");
    };
  }, [resetPingTimeout, clearPingTimeout, lastChatIdRef, lastRequestIdRef]);

  const connect = useCallback(() => {
    if (!currentTokenRef.current) return;
    isManualRef.current = false;
    retryMsRef.current = INITIAL_RETRY_MS;
    connectWs();
  }, [connectWs]);

  const disconnect = useCallback(() => {
    isManualRef.current = true;
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
    setHeartbeatStatus("切断");
  }, []);

  return {
    ws: wsRef.current,
    isConnected,
    isOnline,
    setIsOnline,
    error,
    setError,
    heartbeatStatus,
    setHeartbeatStatus,
    connect,
    disconnect,
    resetPingTimeout,
    retryMsRef,
  };
}
