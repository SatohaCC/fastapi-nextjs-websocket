"use client";

import { createContext, useContext } from "react";
import {
  useGlobalChat,
  type UseGlobalChatResult,
} from "../hooks/useGlobalChat";

const GlobalChatContext = createContext<UseGlobalChatResult | null>(null);

interface GlobalChatProviderProps {
  isAuthenticated: boolean;
  children: React.ReactNode;
}

export function GlobalChatProvider({
  isAuthenticated,
  children,
}: GlobalChatProviderProps) {
  const value = useGlobalChat(isAuthenticated);
  return (
    <GlobalChatContext.Provider value={value}>
      {children}
    </GlobalChatContext.Provider>
  );
}

export function useGlobalChatContext(): UseGlobalChatResult {
  const ctx = useContext(GlobalChatContext);
  if (!ctx) {
    throw new Error(
      "useGlobalChatContext must be used within GlobalChatProvider",
    );
  }
  return ctx;
}
