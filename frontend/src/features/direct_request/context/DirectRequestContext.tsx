"use client";

import { createContext, useContext } from "react";
import {
  useDirectRequest,
  type UseDirectRequestResult,
} from "../hooks/useDirectRequest";

const DirectRequestContext = createContext<UseDirectRequestResult | null>(
  null,
);

interface DirectRequestProviderProps {
  isAuthenticated: boolean;
  children: React.ReactNode;
}

export function DirectRequestProvider({
  isAuthenticated,
  children,
}: DirectRequestProviderProps) {
  const value = useDirectRequest(isAuthenticated);
  return (
    <DirectRequestContext.Provider value={value}>
      {children}
    </DirectRequestContext.Provider>
  );
}

export function useDirectRequestContext(): UseDirectRequestResult {
  const ctx = useContext(DirectRequestContext);
  if (!ctx) {
    throw new Error(
      "useDirectRequestContext must be used within DirectRequestProvider",
    );
  }
  return ctx;
}
