"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { dispatch } from "../handlers/dispatcher";
import { type SeqProvider, useConnection } from "../hooks/useConnection";

export type WsHandler<T = unknown> = (data: T, socket: WebSocket) => void;

export interface WebSocketContextValue {
  isConnected: boolean;
  isOnline: boolean;
  error: string | null;
  heartbeatStatus: string;
  syncStatus: string;
  setSyncStatus: (value: string) => void;
  setError: (value: string | null) => void;
  subscribe: (type: string, handler: WsHandler) => () => void;
  registerSeqProvider: (paramName: string, get: SeqProvider) => () => void;
}

const WebSocketContext = createContext<WebSocketContextValue | null>(null);

interface WebSocketProviderProps {
  token: string | null;
  children: React.ReactNode;
}

export function WebSocketProvider({ token, children }: WebSocketProviderProps) {
  const subscribersRef = useRef(new Map<string, Set<WsHandler>>());
  const seqProvidersRef = useRef(new Map<string, SeqProvider>());
  const [syncStatus, setSyncStatus] = useState<string>("未同期");

  const subscribe = useCallback((type: string, handler: WsHandler) => {
    let set = subscribersRef.current.get(type);
    if (!set) {
      set = new Set();
      subscribersRef.current.set(type, set);
    }
    set.add(handler);
    return () => {
      const current = subscribersRef.current.get(type);
      current?.delete(handler);
      if (current && current.size === 0) {
        subscribersRef.current.delete(type);
      }
    };
  }, []);

  const registerSeqProvider = useCallback(
    (paramName: string, get: SeqProvider) => {
      seqProvidersRef.current.set(paramName, get);
      return () => {
        seqProvidersRef.current.delete(paramName);
      };
    },
    [],
  );

  const {
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
  } = useConnection({
    token,
    seqProvidersRef,
    onMessage: (event, socket) => {
      dispatch(event, socket, {
        subscribers: subscribersRef.current,
        resetPingTimeout,
        setHeartbeatStatus,
        setError,
        setSyncStatus,
      });
    },
    onStatusChange: setSyncStatus,
  });

  useEffect(() => {
    setSyncStatus("待機中...");
    if (token) {
      disconnect();
      connect();
    } else {
      disconnect();
    }
  }, [token, connect, disconnect]);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      retryMsRef.current = 1000;
      setSyncStatus("ネットワーク復帰。再接続しています...");
      connect();
    };
    const handleOffline = () => {
      setIsOnline(false);
      setSyncStatus("ネットワークオフライン");
      disconnect();
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, [connect, disconnect, setIsOnline, retryMsRef]);

  const value = useMemo<WebSocketContextValue>(
    () => ({
      isConnected,
      isOnline,
      error,
      heartbeatStatus,
      syncStatus,
      setSyncStatus,
      setError,
      subscribe,
      registerSeqProvider,
    }),
    [
      isConnected,
      isOnline,
      error,
      heartbeatStatus,
      syncStatus,
      setError,
      subscribe,
      registerSeqProvider,
    ],
  );

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocketContext(): WebSocketContextValue {
  const ctx = useContext(WebSocketContext);
  if (!ctx) {
    throw new Error(
      "useWebSocketContext must be used within WebSocketProvider",
    );
  }
  return ctx;
}
