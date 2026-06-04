import type { RefObject } from "react";
import { useCallback, useEffect, useRef, useState } from "react";
import { WS_BASE } from "@/lib/config";

const PING_TIMEOUT_MS = (10 + 5 + 2) * 1000;
const INITIAL_RETRY_MS = 1000;
const MAX_RETRY_MS = 30000;

export type SeqProvider = () => number | null;

interface UseConnectionProps {
  isAuthenticated: boolean;
  seqProvidersRef: RefObject<Map<string, SeqProvider>>;
  onMessage: (event: MessageEvent, socket: WebSocket) => void;
  onStatusChange?: (status: string) => void;
}

export function useConnection({
  isAuthenticated,
  seqProvidersRef,
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

  const currentAuthRef = useRef<boolean>(isAuthenticated);
  currentAuthRef.current = isAuthenticated;

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

  const connectWs = useCallback(async () => {
    const activeAuth = currentAuthRef.current;
    if (!activeAuth) return;

    // 1. BFFからワンタイムチケットを取得
    let ticket: string;
    try {
      const res = await fetch("/api/auth/ws-ticket");
      if (!res.ok) {
        onStatusChangeRef.current?.("認証チケットの取得に失敗しました");
        throw new Error("Failed to get ticket");
      }
      const data = await res.json();
      ticket = data.ticket;
    } catch (_err) {
      setError("WebSocket 認証チケットの取得に失敗しました");
      if (!isManualRef.current) {
        const delay = retryMsRef.current;
        retryMsRef.current = Math.min(delay * 2, MAX_RETRY_MS);
        onStatusChangeRef.current?.(
          `接続失敗。${delay / 1000}秒後に再試行します...`,
        );
        reconnectTimerRef.current = setTimeout(() => {
          connectWs().catch((err) => {
            console.error("[reconnectTimerRef] connectWs failed:", err);
          });
        }, delay);
      }
      return;
    }

    if (wsRef.current) {
      wsRef.current.onclose = null;
      wsRef.current.close();
      wsRef.current = null;
    }

    const url = new URL(`${WS_BASE}/ws`);
    url.searchParams.set("ticket", ticket);
    const providers = seqProvidersRef.current;
    if (providers) {
      for (const [paramName, get] of providers.entries()) {
        const v = get();
        if (v !== null) url.searchParams.set(paramName, v.toString());
      }
    }

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
        reconnectTimerRef.current = setTimeout(() => {
          connectWs().catch((err) => {
            console.error(
              "[reconnectTimerRef] connectWs close reconnect failed:",
              err,
            );
          });
        }, delay);
      }
    };

    socket.onerror = () => {
      setError("WebSocket connection error");
    };
  }, [resetPingTimeout, clearPingTimeout, seqProvidersRef]);

  const connect = useCallback(() => {
    if (!currentAuthRef.current) return;
    isManualRef.current = false;
    retryMsRef.current = INITIAL_RETRY_MS;
    connectWs().catch((err) => {
      console.error("[connectWs] Initial connection failed:", err);
    });
  }, [connectWs]);

  const disconnect = useCallback(() => {
    isManualRef.current = true;
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
    setHeartbeatStatus("切断");
  }, []);

  return {
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
